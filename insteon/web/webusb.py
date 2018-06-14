
class WebUSB:
    def __init__(self):
        pass

    def choose(self):
        import js
        dev_id = 'lkfjasfs'
        js.run('navigator.usb.requestDevice({filters:[]}).then(dev => window.ports.foobar =dev);')
