from distutils.core import setup
import setup_translate

pkg = 'Extensions.EBroadLink'
setup(name='enigma2-plugin-extensions-ebroadlink',
       version='1.0',
       description='Production BroadLink management',
       packages=[pkg],
       package_dir={pkg: 'plugin'},
       package_data={pkg: ['*.png', '*.xml', '*/*.png', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass=setup_translate.cmdclass,
      )
