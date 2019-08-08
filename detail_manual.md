# Pseudo-Lidar on Argoverse Dataset User Manual
This manual details the steps on how to reproduce our work of applying Pseudo-Lidar algorithm to the Argoverse Dataset. 
This work is dedicated on SJSU HPC platform, which integrates a GPU. 

## 1. Get the Pseudo-Lidar repository
Assume your work folder is $ROOT for the following steps. 
```
    cd $ROOT/
    git clone https://github.com/MengshiLi/pseudo_lidar.git
```

## 2. Download the Argoverse Dataset
- Download link to dataset: [Argoverse Data Set Download](https://www.argoverse.org/data.html#download-link)
- Unzip files to the same position, requires 250G+ storage capacity.
- Data path will be represented as `$DATAPATH`. 
- For example, on our HPC: `$DATAPATH=
/data/cmpe297-03-sp19/PilotA/Argoverse_3d_tracking/argoverse-tracking`

## 3. Setup Python virtualenv for Argoverse
- Clone the argoverse api: `git clone https://github.com/MengshiLi/argoverse-api`
- Login to HPC: `ssh <SID>@coe-hpc.sjsu.edu`. (Only for SJSU HPC users)
- The training and inference work will run on the GPU node, but GPU node has no network access. Therefore, the env must be setup from the entrance footholder node:
```
    module load python3/3.7.0
    which python3 #to obtain <absolute-python-path> for python3
    virtualenv --python=<absolute-python-path> venv-3.7-argo
    source ~/venv-3.7-argo/bin/activate
    pip install -e <path_to_root_directory_of_the_repo>
```
- If you want to visualize Lidar with mayavi, find another machine that suports GUI. Execute the following command on top of the above commands:
```
    pip install mayavi
    pip install PyQt5
```
- For more guidelines on mayavi installation, check [here](https://docs.enthought.com/mayavi/mayavi/installation.html).

## 4. Setup Python virtualenv for PSMNet
- PSMNet requires python2 and pytorch, therefore, it is recommanded to setup a separate virtualenv.
- Install from the footholder node:
```
    module load cuda/9.2 python2/2.7.15
    which python #to obtain <absolute-python-path> for python2
    virtualenv --python=<absolute-python-path> venv_PSMNet_cuda
    source ~/venv_PSMNet_cuda/bin/activate
    pip install torch torchvision==0.2.0 scikit-image
```
- Note that torchvision is designated to 0.2.0 manually, as a higher version will errorneously visualize the disparity map.

## 5. Generate groundtruth disparity from Lidar 
- The groundtruth disparity is used to finetuen the PSMNet model. As Argoverse dataset is not providing groundtruth disparity for its stereo images, we will generate them from Lidar.
- Source code for generate disparity: `$ROOT/preprocessing/argo_gen_disp.py`. 
- Run it from any GPU node. Avoid running any heavy load on the footholder node.
- Before running the code, ensure Argoverse dataset is already downloaded and organized in the following format.
```
argoverse-tracking/
    train1/
        log_id11/ # unique log identifier  
            lidar/ # lidar point cloud file in .PC  
            stereo_front_left/ # stereo left image
            stereo_front_right/ # stereo right image
            vehicle_calibration_info.json
        log_id12/
            ...
    train2/ 
        ...
    train4/  
```
- Use screen to avoid task interruption due to shell stall: `screen`
- Obtain the GPU node: `srun -p gpu --gres=gpu --pty /bin/bash`
- From GPU node, activate the Python virtualenv we have installed for Argoverse:
```
	module load python3/3.7.0
	source ~/venv-3.7-argo/bin/activate
	python $ROOT/preprocessing/argo_gen_disp.py --root_dir $DATAPATH
```

## 6. Train: finetune the PSMNet model
- Download the pretrained model: [PSMNet on KITTI2015](https://drive.google.com/file/d/1pHWjmhKMG4ffCrpcsp_MTXMJXhgl3kF9/view?usp=sharing).
- Related source code: 
  - `$ROOT/psmnet/dataloader/ARGOLoader3D.py`
  - `$ROOT/psmnet/dataloader/ARGOLoader_dataset3d.py`
  - `$ROOT/psmnet/finetune_3d_argo.py`


- Launch a GPU node: `srun -p gpu --gres=gpu --pty /bin/bash`, from GPU: 
``` 
    module load cuda/9.2 python2/2.7.15
    source ~/venv_PSMNet_cuda/bin/activate
    python $ROOT/psmnet/finetune_3d_argo.py --loadmodel <path to pretrained model>
```

## 7. Inference: predict disparity from stereo image
Still running from the above virtualenv: 
```
    python $ROOT/psmnet/argo_inference.py --datapath $DATAPATH --sub_folder train4 --loadmodel <finetuned model path>
```

## 8. Generate Pseudo-Lidar from predicted disparity

- Obtain another GPU node: `srun -p gpu --gres=gpu --pty /bin/bash`

- From GPU node, activate the python virtual environment for argoverse:
```
    module load python3/3.7.0
    source ~/venv-3.7-argo/bin/activate
```
- Usage: 
```
    python $ROOT/preprocessing/argo_gen_lidar.py --root_dir $DATAPATH --sub_folder train4
```

## 9. Visuzalize the newly-generated Pseudo-Lidar
Same env as step 8.
- Visualize while generating pseudo-lidar: 
```
    python $ROOT/preprocessing/argo_gen_lidar.py --root_dir $DATAPATH --sub_folder train4 --viz_lidar=True
```

- Visualize Lidar from loading a ply file. 
```
    python $ROOT/preprocessing/argo_viz_lidar.py --root_dir $DATAPATH --sub_folder train4
```

## 10. Apply Pseudo-Lidar to any 3D object-detection model
