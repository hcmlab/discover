"""Custom dependency handling for NOVA-Server modules

Authors:
    Dominik Schiller <dominik.schiller@uni-a.de>,
    Tobias Hallmen <tobias.hallmen@informatik.uni-augsburg.de>
Date:
    13.09.2023
"""

import sys
from pathlib import Path
import subprocess
import site

def assert_or_install_dependencies(packages, trainer_name):
    site_package_path = (
        Path(site.getsitepackages()[0])
        / ".."
        / "nova-server-site-packages"
        / trainer_name
    ).resolve()
    site_package_path.mkdir(parents=True, exist_ok=True)

    #TODO: handle pip install *.zip
    for i, pkg in enumerate(packages):
        params = []
        # split on space while also removing double spaces
        pk = [x for x in pkg.split(" ") if x]
        if len(pk) > 1:
            params.extend(pk[1:])
        # maybe add all VCS https://pip.pypa.io/en/stable/topics/vcs-support/
        if "git+" in pk[0]:
            if "#egg=" in pk[0]:
                name = pk[0].split("#egg=")[-1]
            else:
                name = pk[0].split("/")[-1].split(".git")[0]
        else:
            # maybe support all specifiers https://peps.python.org/pep-0440/#version-specifiers
            name = pk[0].split('==')[0]
            # setup-version-specifier
            if '[' in name:
                name = name[:name.find('[')]

        # support systems without nvidia/cuda installed
        try:
            subprocess.check_output("nvidia-smi")
            cuda_available = True
        except:
            cuda_available = False

        # torch/torchvision/torchaudio
        # remove cuda specific torch wheel params
        if name.startswith("torch") and "+cu" in name and not cuda_available:
            pk[0] = pk[0][: pk[0].find("+cu")]
            for p in pk:
                if "index-url" in p or "download.pytorch.org/whl" in p:
                    params.remove(p)

        # onnxruntime
        if name == 'onnxruntime':
            if cuda_available:
                pk[0] = pk[0].replace('onnxruntime', 'onnxruntime-gpu')
            elif sys.platform == 'darwin':
                pk[0] = pk[0].replace('onnxruntime', 'onnxruntime-silicon')

        params.append("--target={}".format(site_package_path))

        # appears to be pythonic way (snake case)
        if Path(
            "{}/{}".format(
                site_package_path, adjusted_name := str(name).replace("-", "_")
            )
        ).exists() or any(
            adjusted_name in x
            for x in [
                x.name
                for x in Path(f"{site_package_path}").glob(
                    f"{adjusted_name}-*.dist-info"
                )
            ]
        ):
            print(
                f"Skip installation of {site_package_path}/{name} - package already installed"
            )
        # some don't follow it, e.g. pyannote (. instead of _)
        elif Path(
            "{}/{}".format(
                site_package_path, adjusted_name := str(name).replace("-", ".")
            )
        ).exists() or any(
            adjusted_name in x
            for x in [
                x.name
                for x in Path(f"{site_package_path}").glob(
                    f"{adjusted_name}-*.dist-info"
                )
            ]
        ):
            print(
                f"Skip installation of {site_package_path}/{name} - package already installed"
            )
        else:
            install_package(pk[0], params)

    sys.path.insert(0, str(site_package_path.resolve()))


def install_package(pkg, params):
    call = [sys.executable, "-m", "pip", "install", pkg, *params]
    print(*call)
    return subprocess.check_call(call)
