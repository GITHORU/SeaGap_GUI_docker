import docker
from multiprocessing import Process

def plot_ttres():
    try :
        client = docker.from_env()
        cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[r"C:\Users\hugor\Documents\THESE\02_pro\11_Docker\test_folder:/app"])
        cont.exec_run('''julia -e "using SeaGap; SeaGap.ttres(35.0, save=true)"''')
        cont.exec_run('''julia -e "using SeaGap; SeaGap.plot_ttres(show=false)"''')
        cont.stop()
        return True
    except :
        return False


if __name__ == '__main__':
    proc = Process(target=plot_ttres)
    proc.start()
    # proc.join()
    print("OK !")