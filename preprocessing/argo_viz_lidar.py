import os
import argparse
import numpy as np
import argoverse
from argoverse.data_loading.argoverse_tracking_loader import ArgoverseTrackingLoader
from argoverse.visualization.mayavi_utils import draw_lidar, mayavi_compare_point_clouds 
from argoverse.utils.ply_loader import load_ply
from argoverse.utils import mayavi_wrapper

    
# the main routine
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize Lidar')
    parser.add_argument('--root_dir', type=str,
                        default='/Users/mengsli/Downloads/DLRepo/argoverse-tracking/')
    parser.add_argument('--sub_folder', type=str, default='sample/') #train1, train2 ... val, test
    parser.add_argument('--max_high', type=int, default=1)
    args = parser.parse_args()

    assert os.path.isdir(args.root_dir)
    sub_dir = args.root_dir + '/' + args.sub_folder
    
    argoverse_loader = ArgoverseTrackingLoader(sub_dir)
    for log_id in argoverse_loader.log_list:

        pseudo_lidar_dir = sub_dir + '/' + log_id + '/' + 'lidar/' #true lidar for debugging
        #pseudo_lidar_dir = sub_dir + '/' + log_id + '/' + 'pred_lidar/'
        assert os.path.isdir(pseudo_lidar_dir)
        
        lidar_list = [x for x in os.listdir(pseudo_lidar_dir) if x[-3:] == 'ply']
        lidar_list = sorted(lidar_list)

        for fn in lidar_list:
            lidar = load_ply(pseudo_lidar_dir + '/' + fn)
            fig = draw_lidar(lidar)
            mayavi_wrapper.mlab.show()
        
