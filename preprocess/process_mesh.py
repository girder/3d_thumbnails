# -----------------------------------------------------------------------------
# Download data:
#  - Browser:
#      http://midas3.kitware.com/midas/folder/10409 => VisibleMale/vm_head_mri.mha
#  - Terminal
#      curl "http://midas3.kitware.com/midas/download?folders=&items=235237" -o vm_head_mri.mha
# -----------------------------------------------------------------------------

from vtk import *

from vtk.web.query_data_model import *
from vtk.web.dataset_builder import *


import click
import ctypes
from vtk import (
    vtkOBJReader, vtkPolyDataMapper, vtkActor, vtkRenderWindow, vtkRenderer, vtkCamera)

from vtk.web.dataset_builder import ImageDataSetBuilder, update_camera

__version__ = '0.1.0'
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512

# Unfortunately this hack is necessary to get the libOSMesa symbols loaded into
# the global namespace, presumably because they are weakly linked by VTK
ctypes.CDLL('libOSMesa.so', ctypes.RTLD_GLOBAL)


def arc_samples(n_samples):
    step = 360. / n_samples
    return [step * i for i in range(n_samples)]


@click.command()
@click.argument('in_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('out_dir', type=click.Path(file_okay=False))
@click.option('--width', default=DEFAULT_WIDTH, help='output image width (px)')
@click.option('--height', default=DEFAULT_HEIGHT, help='output image height (px)')
@click.option('--phi-samples', default=8, help='number of samples in phi dimension')
@click.option('--theta-samples', default=1, help='number of samples in theta dimension')
@click.version_option(version=__version__, prog_name='Process a volume image into a 3d thumbnail')
def process(in_file, out_dir, width, height, phi_samples, theta_samples):
    phi_vals = arc_samples(phi_samples)
    theta_vals = arc_samples(theta_samples)

    reader = vtkOBJReader()
    reader.SetFileName(in_file)
    reader.Update()

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)

    window = vtkRenderWindow()
    window.SetSize(512, 512)

    renderer = vtkRenderer()
    window.AddRenderer(renderer)

    renderer.AddVolume(actor)

    camera = vtkCamera()
    renderer.SetActiveCamera(camera)

    window.Render()
    renderer.ResetCamera()
    window.Render()

    # Camera setting
    camera = {
        'position': [v for v in camera.GetFocalPoint()],
        'focalPoint': camera.GetFocalPoint(),
        'viewUp': [1,0,0]
    }
    camera['position'][2] += 100
    update_camera(renderer, camera)
    window.Render()
    renderer.ResetCamera()
    window.Render()

    idb = ImageDataSetBuilder(out_dir, 'image/jpg', {
        'type': 'spherical',
        'phi': phi_vals,
        'theta': theta_vals
    })

    idb.start(window, renderer)
    idb.writeImages()
    idb.stop()


if __name__ == '__main__':
    process()
