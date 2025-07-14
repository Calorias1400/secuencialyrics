from setuptools import setup
from py2app.build_app import py2app as build_py2app

# —– Subclase de py2app que ignora el code signing —–
class NoSignPy2app(build_py2app):
    def codesign_adhoc(self, target):
        # Simplemente no hacemos nada, así no falla el firmado
        return

APP = ['script.py']
OPTIONS = {
    # ya habíamos deshabilitado argv_emulation y frameworks
    'includes': ['tkinter'],
    'plist': {
        'CFBundleName': 'AutoPremiereSequence',
        'CFBundleShortVersionString': '1.0',
        'CFBundleIdentifier': 'com.tuempresa.autopremiere',
    },
    # Si quieres icono, añade 'iconfile': 'icon.icns'
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    cmdclass={'py2app': NoSignPy2app},
    setup_requires=['py2app'],
)