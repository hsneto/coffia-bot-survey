import os
import telepot
from time import sleep
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id

from coffiaBot import utils
from coffiaBot.database import query
from coffiaBot import getImageData

# Importa macros
macros = utils.loadMacros()

# # Configura o proxy na API
# telepot.api.set_proxy(macros.bot["proxy"])

# Image filenames
FILENAMES = [os.path.join(macros.photos.get("path"), f) for f in os.listdir(macros.photos.get("path"))]

# Thread-safe dict
propose_records = telepot.helper.SafeDict()  

# Comandos do BOT
commands = utils.toNamedtuple({c : utils.createPattern(c) for c in (
    "iniciar",  # Inicia o processo de rotulação        []
    "parar",     # Interrompe o processo de rotulação    []
)})

class TelegramBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__(*args, **kwargs)

        # Recuperar do banco de dados
        global propose_records

        # Se a conversa com o usuário está em aberto
        if self.id in propose_records:
            self._count, self._edit_msg_ident = propose_records[self.id]
            self._editor = telepot.helper.Editor(self.bot, self._edit_msg_ident) if self._edit_msg_ident else None
        
        # Se a conversa é nova
        else:
            self._edit_msg_ident = None
            self._editor = None
            self._chatState = 0 # Tipo de reply esperada

            # Info do usuario
            self.userId = None
            self.userName = None
            self.userJob = None
            self.userCompany = None

            # Info do survey
            self.imageId = None
            self.labelId = None
     
    def _handle_message(self, msg):
        
        # Ler conteúdo da mensagem
        msgText = msg["text"]
        msgFrom = msg["from"]
        telegramId = msgFrom["id"]

        # Id do usuario no db
        self.userId = query.getUser(telegramId) if not self.userId else self.userId

        # Cadastro de novo usuario
        if not self.userId:
            self.cmdAddUser(msgText, telegramId)

        else:
            # COMANDO: /parar
            if utils.matchPattern(msgText, commands.parar):
                self.cmdStop()

            # COMANDO: /iniciar
            elif utils.matchPattern(msgText, commands.iniciar):
                self.cmdStart()

            # COMANDO: <invalido>
            else:
                self.sender.sendMessage("Comando inválido!")
                self.close()

    def _cancel_last(self):
        if self._editor:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_msg_ident = None

    def on_callback_query(self, msg):
        _, _, queryData = telepot.glance(msg, flavor='callback_query')

        if self._chatState == 2:
            
            self._cancel_last()
            query.addSurvey(self.userId, self.imageId, queryData)
            self.sender.sendMessage(
                f"Imagem {self.imageId} possui {query.getLabelName(queryData)}"
                " de frutos maduros.")

            self._chatState = 1 # restart survey
            self.cmdSendPhoto()

        # COMANDO: <invalido>
        else:
            self._cancel_last()
            self.sender.sendMessage("Opção do teclado desconhecida.")
            self.close()

    def on_chat_message(self, msg):
        content_type, _, _ = telepot.glance(msg)
        if content_type == "text":
            self._handle_message(msg)

    def on__idle(self, event):
        self.sender.sendMessage("Tempo esgotado! Envia /iniciar pare recomeçar.")
        self.close()

    def on_close(self, ex):
        global propose_records

    def cmdStop(self):
        self._cancel_last()
        self.sender.sendMessage("Muito obrigado pela sua participação!.")
        self.sender.sendMessage(
            "Se quiser voltar a ajudar na pesquisa, "
            "basta enviar o comando /iniciar.")
        self.close()

    def cmdSendPhoto(self):
        self.imageId, f = getImageData(FILENAMES)
        self.sender.sendPhoto(open(f, "rb"))
        
        sent = self.sender.sendMessage(
            "Selecione o intervalo que represente a porcentagem de frutos "
            "maduros na imagem acima:", 
        reply_markup=query.getKeybordLabels())
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_msg_ident = telepot.message_identifier(sent)

        self._chatState = 2

    def cmdStart(self):
        self.sender.sendMessage(
            "Eu vou te enviar algumas imagens de plantas de cafés e vou te "
            "pedir para usar os seus conhecimentos e experiências para "
            "classificar a porcentagem de frutos maduros nela.")

        self.sender.sendMessage(
            "Caso queira para, basta enviar o comando /parar ou esperar 5 "
            "minutos para a conversa se encerrar.")
        self.cmdSendPhoto()

    def cmdAddUser(self, msgText, telegramId):
        if self._chatState == 0:
            self.sender.sendMessage(
                "Olá!\nAcabei de consultar meu banco de dados e não te "
                "encontrei.\nVocê pode me informar o seu nome?")
            self._chatState = 1

        elif self._chatState == 1:
            self.userName = msgText
            username = self.userName.split(" ")[0]
            self.sender.sendMessage(
                f"Ei {username}. Prazer em te conhecer.\nAinda preciso de mais "
                "algumas informações. Pode me contar qual o seu emprego/função?")
            self._chatState = 2

        elif self._chatState == 2:
            self.userJob = msgText
            self.sender.sendMessage(
                "Estamos quase terminando.\n"
                "Só preciso saber o nome da empresa em que trabalha.")
            self._chatState = 3

        elif self._chatState == 3:
            self.userCompany = msgText
            query.addUser(
                self.userName, self.userJob, self.userCompany, telegramId)
            self.sender.sendMessage("Show, obrigado por se cadastrar.")
            self.sender.sendMessage(
                "Para começar a pesquisa, basta enviar o comando /iniciar.")
            self.close()

        else:
            self.sender.sendMessage(
                "Algo inesperado aconteceu. Por favor tente novamente.")
            self.close()


bot = telepot.DelegatorBot(macros.bot["token"], [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, TelegramBot, timeout=macros.bot.get("timeout", 300)),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while True:
    sleep(macros.bot.get("timeout", 300))
