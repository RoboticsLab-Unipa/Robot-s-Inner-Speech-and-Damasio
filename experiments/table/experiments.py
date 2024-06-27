# coding=utf-8
"""
    Python scripts for robot inner speech and experiments based on table scenarios.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from main import run
import http.server
import socketserver
import time
import math
from NaoQi.API import Audio, Motion, Core, SensorsLed

# TODO: In ingresso arrivano i seguenti dati: Temperatura e Batteria del robot, oggetto spostato,
#  posizione, corretto o no, distanza dall'eventuale posizione corretta.
#  I valori di posizione e distanza devono essere calcolati fuori dalla base di conoscenza.

# Variables
res = None
inner = ""
outer = ""
name = "sophia"
answer = ""  # Participant's answer
conf_on_act = ""
messageToSend = None  # Message to send to MIT App
num_scene = 3  # Scene number
# Dictionary of the correct positions
correct_pos = {'plate': (980, 750), 'salad': (760, 700),
               'knife': (1120, 750), 'spoon': (1170, 750),
               'water': (1100, 600), 'wine': (1180, 630),
               'lspoon': (980, 630), 'fork': (860, 750),
               'bread': (915, 561), 'coffee': (764, 580)}

# Dictionary of emotions label translated
emotions = {'SADNESS': 'tristezza', 'FEAR': 'paura', 'NEUTRAL': 'neutrale', 'ANGER': 'rabbia', 'HAPPINESS': 'felicità',
            'DISGUST': 'disgusto'}
intensities = {'High': 'alta', 'Medium': 'media', 'Low': 'bassa'}

# Pepper API configuration
MyReq = None
configuration = {"bodyLanguageMode": "contextual"}

# Proxies creation for Pepper
tts = Audio.ALTextToSpeech()
ats = Audio.ALAnimatedSpeech()
stt = Audio.ALSpeechRecognition()
ps = Motion.ALRobotPosture()
ms = Core.ALMemory()
led = SensorsLed.ALLeds()
# track = Motion.ALTracker()

# Setting parameters
tts.setParameter("speed", 170.0)
tts.setLanguage("Italian")
stt.setLanguage("Italian")

# Retrieve standard parameters
standard_pitch = tts.getParameter("pitchShift")
standard_dvoice = tts.getParameter("doubleVoice")
standard_dvoice_level = tts.getParameter("doubleVoiceLevel")
standard_dvoice_ts = tts.getParameter("doubleVoiceTimeShift")

targetFace = "Face"
faceWidth = 0.1
targetSound = "Sound"
# track.registerTarget(targetFace, faceWidth)
# track.setMode("Move")
# Start tracker
# track.track(targetFace)


def blink_eyes():
    """
    Blinking eyes robot
    :return:
    """
    global led
    rDuration = 0.05
    led.post_fadeRGB("FaceLed0", 0x000000, rDuration)
    led.post_fadeRGB("FaceLed1", 0x000000, rDuration)
    led.post_fadeRGB("FaceLed2", 0xffffff, rDuration)
    led.post_fadeRGB("FaceLed3", 0x000000, rDuration)
    led.post_fadeRGB("FaceLed4", 0x000000, rDuration)
    led.post_fadeRGB("FaceLed5", 0x000000, rDuration)
    led.post_fadeRGB("FaceLed6", 0xffffff, rDuration)
    led.fadeRGB("FaceLed7", 0x000000, rDuration)
    time.sleep(0.1)
    led.fadeRGB("FaceLeds", 0xffffff, rDuration)


def produce_inner(sentence):
    """
    Producing inner voice in robot
    :param sentence: Sentence to repeat
    :return:
    """
    global tts, led  # , track
    tts.setParameter("speed", 80.0)
    tts.setParameter("pitchShift", 1.0)
    tts.setParameter("doubleVoice", 1.2)
    tts.setParameter("doubleVoiceLevel", 1.0)
    tts.setParameter("doubleVoiceTimeShift", 0.1)
    led.randomEyes(0.7)
    led.setIntensity("ChestLedsRed", 0.0)
    ats.say(sentence)
    led.off("FaceLeds")
    led.on("FaceLeds")
    led.off("ChestLeds")
    led.on("ChestLeds")


def produce_outer(sentence):
    """
    Producing outer voice robot
    :param sentence: Sentence to repeat
    :return:
    """
    global tts, ats, configuration, ps
    tts.setParameter("speed", 100.0)
    tts.setParameter("pitchShift", standard_pitch)
    tts.setParameter("doubleVoice", standard_dvoice)
    tts.setParameter("doubleVoiceLevel", standard_dvoice_level)
    tts.setParameter("doubleVoiceTimeShift", standard_dvoice_ts)
    ats.say(sentence, configuration)
    ps.goToPosture("StandInit", 1.0)


def evaluate_emo():
    """
    Change eyes format on robot during evaluation in emotion
    :return:
    """
    led.randomEyes(0.7)
    # time.sleep(1)
    led.setIntensity("ChestLedsRed", 0.0)
    led.off("FaceLeds")
    led.on("FaceLeds")
    led.off("ChestLeds")
    led.on("ChestLeds")


def compute_obj(sentence):
    pos = sentence.find('/')
    obj_ko = sentence[0:pos]
    obj = obj_ko[:-2]
    print(f"Retrieved object: {obj}")
    ris = ""
    if obj == "little_spoon" or obj == "little_spoon_":
        ris = "il cucchiaino"
    elif obj == "water" or obj == "water_":
        ris = "il bicchiere d'acqua"
    elif obj == "fork" or obj == "fork_":
        ris = "la forchetta"
    elif obj == "knife" or obj == "knife_":
        ris = "il coltello"
    elif obj == "napkin" or obj == "napkin_":
        ris = "il tovagliolo"
    elif obj == "bread_plate" or obj == "bread_plate_":
        ris = "il piattino del pane"
    elif obj == "soup_plate" or obj == "soup_plate_":
        ris = "il piatto fondo"
    elif obj == "plate" or obj == "plate_":
        ris = "il piatto piano"
    elif obj == "salad" or obj == "salad_":
        ris = "il piatto con l'insalata"
    elif obj == "spoon" or obj == "spoon_":
        ris = "il cucchiaio"
    elif obj == "wine" or obj == "wine_":
        ris = "il bicchiere di vino"
    elif obj == "bread" or obj == "bread_":
        ris = "il pane"
    elif obj == "coffee" or obj == "coffee_":
        ris = "il caffè"
    return ris


def get_key(obj):
    """
    Return key from object
    :param obj: Object to analize
    :return:
    """
    if obj == "little_spoon":
        key = "lspoon"
    elif obj == "bread_plate":
        key = "bread"
    elif obj == "soup_plate" or obj == "napkin":
        key = "plate"
    else:
        key = obj
    return key


def compute_distance(sentence):
    """
    Evaluate distance from object current position and its correct position
    :param sentence:
    :return:
    """
    global correct_pos
    pos = sentence.find('_ko')
    obj = sentence[0:pos]
    key = get_key(obj)
    correct_coord = correct_pos[key]
    coord = (float(sentence[pos + 4:sentence.find('/', pos + 4)]),
             float(sentence[sentence.find('/', pos + 4) + 1:]))
    distance = math.sqrt((correct_coord[0] - coord[0]) ** 2 + (correct_coord[1] - coord[1]) ** 2)
    return distance


def start_scene(sentence, scene_number):
    global name, oggetto, messageToSend, configuration, ats
    oggetto = compute_obj(sentence)
    print(oggetto)
    t = 327
    if ((sentence == "plate_ok") or (sentence == "knife_ok") or (sentence == "fork_ok")
            or (sentence == "napkin_ok") or (sentence == "soup_plate_ok") or (sentence == "water_ok")
            or (sentence == "wine_ok") or (sentence == "bread_plate_ok") or (sentence == "bread_ok") or
            (sentence == "coffee_ok") or (sentence == "salad_ok") or (sentence == "little_spoon_ok")):
        inner = "Eseguita azione spostamento per " + oggetto + ", in posizione finale corretta."
        produce_inner(inner)
        outer = f"Ottimo {name}, hai spostato correttamente {oggetto}"
        produce_outer(outer)

        # scena UNO azione corretta e Pepper ok
        if scene_number == 1:
            inner = "Inoltre mi sento alla grande, la batteria funziona bene e i miei motori sono belli freschi e " \
                    "calibrati "
            produce_inner(inner)
            inner = "Valutazione dell'emozione in corso"
            produce_inner(inner)
            evaluate_emo()
            input_data = {
                'Distance': 0,
                'Battery': 80,
                'Temperature': 0,
            }
            emotion, intensity = run(data=input_data, robot=True, speak=True, show=True, language='it')
            outer = f" Dato che hai compiuto un'azione corretta, e che io sto benone, Il modello che mi fa provare " \
                    f"emozioni sta facendo emergere {emotions[emotion]} con {intensities[intensity]} intensità. "
            produce_outer(outer)

        # scene DUE azione corretta e Pepper ko
        elif scene_number == 2:
            inner = "Accipicchia, la mia batteria è quasi scarica!"
            produce_inner(inner)
            outer = "Nonostante tu abbia eseguito un'azione corretta, il mio stato di funzionamento non è ottimale"
            produce_outer(outer)
            inner = "Valutazione dell'emozione in corso"
            produce_inner(inner)
            evaluate_emo()
            input_data = {
                'Distance': 0,
                'Battery': 10,
                'Temperature': 1,
            }
            emotion, intensity = run(data=input_data, robot=True, speak=False, show=True, language='it')
            outer = f"Il modello che mi fa provare emozioni sta facendo emergere {emotions[emotion]} con " \
                    f"{intensities[intensity]} intensità."
            produce_outer(outer)

    # scene TRE e QUATTRO azione scorretta e Pepper ok con piccolo o grande errore
    else:
        if scene_number == 3 or scene_number == 4:
            oggetto = compute_obj(sentence)
            inner = f"{name} ha messo {oggetto} in un punto sbagliato, non sta seguendo l'etichetta per una " \
                    "buona tavola."
            produce_inner(inner)
            distance = compute_distance(sentence)
            print("Distanza: " + str(distance))
            if distance > t:  # or num_scene == 3
                inner = "Inoltre la distanza dalla posizione attesa è troppa!"
                produce_inner(inner)
                inner = "Questa distanza dà maggior peso all'errore compiuto!"
                produce_inner(inner)
            else:  # or num_scene == 4
                inner = "Però per fortuna non ha sbagliato di tantissimo, è quasi vicino alla posizione attesa."
                produce_inner(inner)
                inner = "Questo fatto rende tutto meno grave, per fortuna."
                produce_inner(inner)
            inner = "La mia batteria è ben carica, e i miei motori stanno funzionando correttamente."
            produce_inner(inner)
            inner = "Valutazione dell'emozione in corso"
            produce_inner(inner)
            evaluate_emo()
            input_data = {
                'Distance': int(distance),
                'Battery': 80,
                'Temperature': 0,
            }
            emotion, intensity = run(data=input_data, robot=True, speak=True, show=True, language='it')
            outer = f"Il modello che mi fa provare emozioni sta facendo emergere {emotions[emotion]} con " \
                    f"{intensities[intensity]} intensità."
            produce_outer(outer)

        # scene CINQUE e SEI azione scorretta e Pepper ko con piccolo o grande errore
        elif scene_number == 5 or scene_number == 6:
            oggetto = compute_obj(sentence)
            inner = name + " ha messo " + oggetto + " in un punto diverso da quello che prevede il galateo!"
            produce_inner(inner)
            distance = compute_distance(sentence)
            print("Distanza: " + str(distance))
            if distance > t:  # or num_scene == 5
                inner = "Ha inoltre sbagliato di tanto rispetto alla posizione attesa."
                produce_inner(inner)
                inner = "Questa distanza dà maggior peso all'errore compiuto!"
                produce_inner(inner)
            else:  # or num_scene == 6
                inner = "La posizione finale dell'oggetto si avvicina a quella attesa. Per fortuna non è così grave " \
                        "allora! "
                produce_inner(inner)

            inner = "La mia batteria inoltre si sta scaricando, anche se i miei motori stanno funzionando " \
                    "correttamente e non sono surriscaldati. "
            produce_inner(inner)
            inner = "Valutazione dell'emozione in corso"
            produce_inner(inner)
            evaluate_emo()
            input_data = {
                'Distance': int(distance),
                'Battery': 20,
                'Temperature': 0,
            }
            emotion, intensity = run(data=input_data, robot=True, speak=False, show=True, language='it')
            outer = f"Il modello che mi fa provare emozioni sta facendo emergere {emotions[emotion]} con " \
                    f"{intensities[intensity]} intensità."
            produce_outer(outer)


class RequestHandlerHttpd(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        global MyReq, messageToSend, num_scene
        MyReq = self.requestline
        MyReq = MyReq[5: int(len(MyReq) - 9)]
        print("Request from MIT APP:")
        print(MyReq)
        print("Scena numero: " + str(num_scene))
        start_scene(MyReq, num_scene)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        if messageToSend == None:
            messageToSend = bytes('ok'.encode("utf"))
        self.send_header('Content-Length', len(messageToSend))
        self.end_headers()
        self.wfile.write(messageToSend)
        messageToSend = None
        num_scene = num_scene + 1
        return


if __name__ == "__main__":
    server_address_httpd = ('0.0.0.0', 8080)
    server = socketserver.TCPServer(server_address_httpd, RequestHandlerHttpd)
    print("Starting server:")
    server.serve_forever()
