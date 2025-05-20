# Scilence Detector
Scilence Detector is a little script to monitor some input and send OSC messages on detecting scilence

# For ASIO Support
for pyaudio to support ASIO you need to compile PortAudio with ASIO support enabled 

https://portaudio.com/docs/v19-doxydocs/compile_windows_asio_msvc.html

    python setup.py build_ext -I .\portaudio\include -L .\portaudio\mybuild\Release -l portaudio_x86
    python setup.py install


credit also goes to: https://stackoverflow.com/users/9314452/gwang-jin
https://stackoverflow.com/questions/26391055/multichannel-pyaudio-with-asio-support
