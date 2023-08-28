from threading import Thread
import customtkinter
from vrct_gui import vrct_gui
from config import config
from model import model

# func transcription send message
def sendMicMessage(message):
    if len(message) > 0:
        translation = ""
        if model.checkKeywords(message):
            logDetectWordFilter(message)
            return
        elif config.ENABLE_TRANSLATION is False:
            pass
        elif model.getTranslatorStatus() is False:
            logAuthenticationError()
        else:
            translation = model.getInputTranslate(message)

        if config.ENABLE_TRANSCRIPTION_SEND is True:
            if config.ENABLE_OSC is True:
                if len(translation) > 0:
                    osc_message = config.MESSAGE_FORMAT.replace("[message]", message)
                    osc_message = osc_message.replace("[translation]", translation)
                else:
                    osc_message = message
                model.oscSendMessage(osc_message)
            else:
                logOSCError()

            logSendMessage(message, translation)

def startTranscriptionSendMessage():
    model.startMicTranscript(sendMicMessage)
    vrct_gui.changeMainWindowWidgetsStatus("normal", "All")

def stopTranscriptionSendMessage():
    model.stopMicTranscript()
    vrct_gui.changeMainWindowWidgetsStatus("normal", "All")

# func transcription receive message
def receiveSpeakerMessage(message):
    if len(message) > 0:
        translation = ""
        if config.ENABLE_TRANSLATION is False:
            pass
        elif model.getTranslatorStatus() is False:
            logAuthenticationError()
        else:
            translation = model.getOutputTranslate(message)

        if config.ENABLE_TRANSCRIPTION_RECEIVE is True:
            if config.ENABLE_NOTICE_XSOVERLAY is True:
                xsoverlay_message = config.MESSAGE_FORMAT.replace("[message]", message)
                xsoverlay_message = xsoverlay_message.replace("[translation]", translation)
                model.notificationXSOverlay(xsoverlay_message)
            logReceiveMessage(message, translation)

def startTranscriptionReceiveMessage():
    model.startSpeakerTranscript(receiveSpeakerMessage)
    vrct_gui.changeMainWindowWidgetsStatus("normal", "All")

def stopTranscriptionReceiveMessage():
    model.stopSpeakerTranscript()
    vrct_gui.changeMainWindowWidgetsStatus("normal", "All")

# func message box
def sendChatMessage(message):
    if len(message) > 0:
        translation = ""
        if config.ENABLE_TRANSLATION is False:
            pass
        elif model.getTranslatorStatus() is False:
            logAuthenticationError()
        else:
            translation = model.getInputTranslate(message)

        # send OSC message
        if config.ENABLE_OSC is True:
            if len(translation) > 0:
                osc_message = config.MESSAGE_FORMAT.replace("[message]", message)
                osc_message = osc_message.replace("[translation]", translation)
            else:
                osc_message = message
            model.oscSendMessage(osc_message)
        else:
            logOSCError()

        # update textbox message log
        logSendMessage(message, translation)

        # delete message in entry message box
        if config.ENABLE_AUTO_CLEAR_CHATBOX is True:
            entry_message_box = getattr(vrct_gui, "entry_message_box")
            entry_message_box.delete(0, customtkinter.END)

def messageBoxPressKeyEnter(e):
    model.oscStopSendTyping()
    entry_message_box = getattr(vrct_gui, "entry_message_box")
    message = entry_message_box.get()
    sendChatMessage(message)

def messageBoxPressKeyAny(e):
    model.oscStartSendTyping()
    entry_message_box = getattr(vrct_gui, "entry_message_box")
    if e.keysym != "??":
        if len(e.char) != 0 and e.keysym in config.BREAK_KEYSYM_LIST:
            entry_message_box.insert("end", e.char)
            return "break"

def foregroundOffForcefully(e):
    if config.ENABLE_FOREGROUND:
        vrct_gui.attributes("-topmost", False)

def foregroundOnForcefully(e):
    if config.ENABLE_FOREGROUND:
        vrct_gui.attributes("-topmost", True)

# func print textbox
def logTranslationStatusChange():
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    if config.ENABLE_TRANSLATION is True:
        vrct_gui.printToTextbox(textbox_all, "翻訳機能をONにしました", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "翻訳機能をONにしました", "", "INFO")
    else:
        vrct_gui.printToTextbox(textbox_all, "翻訳機能をOFFにしました", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "翻訳機能をOFFにしました", "", "INFO")

def logTranscriptionSendStatusChange():
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    if config.ENABLE_TRANSCRIPTION_SEND is True:
        vrct_gui.printToTextbox(textbox_all, "Voice2chatbox機能をONにしました", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "Voice2chatbox機能をONにしました", "", "INFO")
    else:
        vrct_gui.printToTextbox(textbox_all, "Voice2chatbox機能をOFFにしました", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "Voice2chatbox機能をOFFにしました", "", "INFO")

def logSendMessage(message, translate):
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_sent = getattr(vrct_gui, "textbox_sent")
    vrct_gui.printToTextbox(textbox_all, message, translate, "SEND")
    vrct_gui.printToTextbox(textbox_sent, message, translate, "SEND")

def logReceiveMessage(message, translate):
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_sent = getattr(vrct_gui, "textbox_received")
    vrct_gui.printToTextbox(textbox_all, message, translate, "RECEIVE")
    vrct_gui.printToTextbox(textbox_sent, message, translate, "RECEIVE")

def logDetectWordFilter(message):
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    vrct_gui.printToTextbox(textbox_all, f"Detect WordFilter :{message}", "", "INFO")
    vrct_gui.printToTextbox(textbox_system, f"Detect WordFilter :{message}", "", "INFO")

def logAuthenticationError():
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    vrct_gui.printToTextbox(textbox_all, "Auth Key or language setting is incorrect", "", "INFO")
    vrct_gui.printToTextbox(textbox_system, "Auth Key or language setting is incorrect", "", "INFO")

def logOSCError():
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    vrct_gui.printToTextbox(textbox_all, "OSC is not enabled, please enable OSC and rejoin", "", "INFO")
    vrct_gui.printToTextbox(textbox_system, "OSC is not enabled, please enable OSC and rejoin", "", "INFO")

def logForegroundStatusChange():
    textbox_all = getattr(vrct_gui, "textbox_all")
    textbox_system = getattr(vrct_gui, "textbox_system")
    if config.ENABLE_FOREGROUND is True:
        vrct_gui.printToTextbox(textbox_all, "Start foreground", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "Start foreground", "", "INFO")
    else:
        vrct_gui.printToTextbox(textbox_all, "Stop foreground", "", "INFO")
        vrct_gui.printToTextbox(textbox_system, "Stop foreground", "", "INFO")

# command func
def toggleTranslationFeature():
    config.ENABLE_TRANSLATION = getattr(vrct_gui, "translation_switch_box").get()
    logTranslationStatusChange()

def toggleTranscriptionSendFeature():
    vrct_gui.changeMainWindowWidgetsStatus("disabled", "All")
    config.ENABLE_TRANSCRIPTION_SEND = getattr(vrct_gui, "transcription_send_switch_box").get()
    if config.ENABLE_TRANSCRIPTION_SEND is True:
        th_startTranscriptionSendMessage = Thread(target=startTranscriptionSendMessage)
        th_startTranscriptionSendMessage.daemon = True
        th_startTranscriptionSendMessage.start()
    else:
        th_stopTranscriptionSendMessage = Thread(target=stopTranscriptionSendMessage)
        th_stopTranscriptionSendMessage.daemon = True
        th_stopTranscriptionSendMessage.start()
    logTranscriptionSendStatusChange()

def toggleTranscriptionReceiveFeature():
    vrct_gui.changeMainWindowWidgetsStatus("disabled", "All")
    config.ENABLE_TRANSCRIPTION_RECEIVE = getattr(vrct_gui, "transcription_receive_switch_box").get()
    if config.ENABLE_TRANSCRIPTION_RECEIVE is True:
        th_startTranscriptionReceiveMessage = Thread(target=startTranscriptionReceiveMessage)
        th_startTranscriptionReceiveMessage.daemon = True
        th_startTranscriptionReceiveMessage.start()
    else:
        th_stopTranscriptionReceiveMessage = Thread(target=stopTranscriptionReceiveMessage)
        th_stopTranscriptionReceiveMessage.daemon = True
        th_stopTranscriptionReceiveMessage.start()
    logTranscriptionSendStatusChange()

def toggleForegroundFeature():
    config.ENABLE_FOREGROUND = getattr(vrct_gui, "foreground_switch_box").get()
    if config.ENABLE_FOREGROUND is True:
        vrct_gui.attributes("-topmost", True)
    else:
        vrct_gui.attributes("-topmost", False)
    logForegroundStatusChange()

# create GUI
vrct_gui.createGUI()

# init config
if model.authenticationTranslator() is False:
    # error update Auth key
    logAuthenticationError()

# set word filter
model.addKeywords()

# check OSC started
model.checkOSCStarted()

# check Software Updated
model.checkSoftwareUpdated()

# set commands
translation_switch_box = getattr(vrct_gui, "translation_switch_box")
translation_switch_box.configure(command=toggleTranslationFeature)
transcription_send_switch_box = getattr(vrct_gui, "transcription_send_switch_box")
transcription_send_switch_box.configure(command=toggleTranscriptionSendFeature)
transcription_receive_switch_box = getattr(vrct_gui, "transcription_receive_switch_box")
transcription_receive_switch_box.configure(command=toggleTranscriptionReceiveFeature)
foreground_switch_box = getattr(vrct_gui, "foreground_switch_box")
foreground_switch_box.configure(command=toggleForegroundFeature)

entry_message_box = getattr(vrct_gui, "entry_message_box")
entry_message_box.bind("<Return>", messageBoxPressKeyEnter)
entry_message_box.bind("<Any-KeyPress>", messageBoxPressKeyAny)
entry_message_box.bind("<FocusIn>", foregroundOffForcefully)
entry_message_box.bind("<FocusOut>", foregroundOnForcefully)

if __name__ == "__main__":
    vrct_gui.startMainLoop()