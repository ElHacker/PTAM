import sh
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from pythonforandroid.logger import info

class Kivy3Recipe(PythonRecipe):
    version = 'master'
    url = 'https://github.com/nskrypnik/kivy3/zipball/{version}/nskrypnik-kivy3-1c050b9.zip'

    depends = ['python2', 'kivy', 'setuptools']

    site_packages_name = 'kivy3'

    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def prebuild_arch(self, arch):
        super(Kivy3Recipe, self).prebuild_arch(arch)

    # def postbuild_arch(self, arch):
        # super(Kivy3Recipe, self).postbuild_arch(arch)
        # print("====================HERE==================")
        # import os
        # print(os.listdir(self.ctx.dist_dir))
        # import shutil
        # shutil.copyfile(
                # self.ctx.build_dir + '/other_builds/kivy3/armeabi-v7a/kivy3/kivy3/default.glsl',
                # self.ctx.dist_dir + '/' + self.ctx.dist_name + '/private/lib/python2.7/site-packages/kivy3/default.glsl')

    def get_recipe_env(self, arch):
        env = super(Kivy3Recipe, self).get_recipe_env(arch)
        # We add BUILDLIB_PATH to PYTHONPATH so twisted can find _io.so
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        return env

    def install_python_package(self, arch):
        '''Automate the installation of a Python package.'''
        env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

recipe = Kivy3Recipe()
