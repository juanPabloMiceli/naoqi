from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "192.168.0.171", 9559)
tts.say("I am chooky and this is day: 1")
