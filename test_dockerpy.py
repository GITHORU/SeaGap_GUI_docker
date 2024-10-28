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

def process_func(*args):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=["C:/Users/hugor/Documents/THESE/02_pro/11_Docker/test_folder:/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.static_individual({0}, [{1}])' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()


if __name__ == '__main__':
    proc1 = Process(target=process_func, args=(35.0, 3.0))
    proc1.start()
    proc2 = Process(target=process_func, args=(35.0, 3.0))
    proc2.start()
    proc3 = Process(target=process_func, args=(35.0, 3.0))
    proc3.start()
    # proc.join()
    print("OK !")

    # process_func(35.0, 3.0)