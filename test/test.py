import sys
import os.path
import logging
import trimesh
import pyrender
import numpy as np
from ruamel.yaml import YAML
ROOT_PATH = r'H:\Robot\easy-dexnet'
sys.path.append(os.path.abspath(os.path.join(ROOT_PATH, 'src')))
try:
    import easydexnet as dex
except Exception as e:
    pass

# 测试一下github的同步功能，这段文字来自于ubuntu


TEST_OBJ_FILE = os.path.join(ROOT_PATH, r'data/test.obj')
TEST_LOG_FILE = os.path.join(ROOT_PATH, 'test/test.log')
TEST_CFG_FILE = os.path.join(ROOT_PATH, 'config/test.yaml')


def config_logging(file=None, level=logging.DEBUG):
    """ 配置全局的日志设置 """
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=file, level=level,
                        format=LOG_FORMAT, filemode='w')


def load_config(file):
    """ 加载配置文件 """
    yaml = YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
    with open(file, 'r', encoding="utf-8") as f:
        config = yaml.load(f)
    return config

def display(mesh, grasps, quality_s=None):
    scene = dex.DexScene(ambient_light=[0.02, 0.02, 0.02],
                         bg_color=[1.0, 1.0, 1.0])
    scene.add_obj(mesh)
    if quality_s is None:
        quality_s = [1] * len(grasps)
    for g,q in zip(grasps, quality_s):
        c = q * np.array([255, 0, -255]) + np.array([0, 0, 255])
        c = np.concatenate((c,[255]))
        c = c.astype(int)
        scene.add_grasp(g, color=c)
        scene.add_grasp_center(g)
    pyrender.Viewer(scene, use_raymond_lighting=True)


def main():
    config_logging(TEST_LOG_FILE)
    config = load_config(TEST_CFG_FILE)
    file_name = os.path.splitext(os.path.basename(TEST_OBJ_FILE))[0]
    print('初始配置成功')

    tri_mesh = trimesh.load_mesh(TEST_OBJ_FILE, validate=True)
    dex_obj = dex.DexObject.from_trimesh(tri_mesh, config, name=file_name)
    quality = dex_obj.qualitis
    quality_s = (quality - np.min(quality)) / (np.max(quality) - np.min(quality))
    display(dex_obj.mesh, dex_obj.grasps, quality_s)
    pose = dex_obj.poses[0]
    grasps = []
    quality = []
    for g,q in zip(dex_obj.grasps,quality_s):
        if g.check_approach(dex_obj.mesh, pose, config) and \
            g.get_approch(pose)[1] < 40:
            grasps.append(g.apply_transform(pose.matrix))
            quality.append(q)
    mesh = dex_obj.mesh.apply_transform(pose.matrix)
    display(mesh, grasps, quality)
    
if __name__ == "__main__":
    
    # print()
    main()
