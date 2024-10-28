import docker, os
def ttres_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"])+":/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.ttres({0}, [{1}], fn1=\"{2}\", fn2=\"{3}\", fn3=\"{4}\", fn4=\"{5}\", fno=\"{6}\", fno0=\"{7}\", save=true)' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    fn0 = args[6]
    fn = os.path.splitext(args[6])[0]+".png"
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.plot_ttres(fn=\"{0}\", fn0=\"{1}\", show=false)' '''.format(fn, fn0), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()

def static_array_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"]) + ":/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.static_array({0}, [{1}], {2}, fn1=\"{3}\", fn2=\"{4}\", fn3=\"{5}\", fn4=\"{6}\", eps={7}, ITMAX={8}, delta_pos={9}, fno0=\"{10}\", fno1=\"{11}\", fno2=\"{12}\", fno3=\"{13}\", fno4=\"{14}\", fno5=\"{15}\")' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()

def static_individual_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"])+":/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.static_individual({0}, [{1}], {2}, fn1=\"{3}\", fn2=\"{4}\", fn3=\"{5}\", fn4=\"{6}\", eps={7}, ITMAX={8}, delta_pos={9}, fno0=\"{10}\", fno1=\"{11}\", fno2=\"{12}\", fno3=\"{13}\", fno4=\"{14}\")' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()
    # self.buttonBox.setDisabled(False)

