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

def static_array_grad_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"]) + ":/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.static_array_grad({0}, [{1}], {2}, fn1=\"{3}\", fn2=\"{4}\", fn3=\"{5}\", fn4=\"{6}\", ITMAX={7}, delta_pos={8}, fno0=\"{9}\", fno1=\"{10}\", fno2=\"{11}\", fno3=\"{12}\", fno4=\"{13}\")' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()

def static_array_mcmcgradv_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"]) + ":/app"])

    _, stream = cont.exec_run('''
    julia -p 4 -t 4 -e
    'using SeaGap;
    SeaGap.static_array_s({0}, [{2}], {3}, {4}, {5}, fn1=\"{8}\", fn2=\"{9}\", fn3=\"{10}\", fn4=\"{11}\", fno0=\"{12}\", fno1=\"{13}\", fno2=\"{14}\", fno3=\"{15}\", fno4=\"{16}\", fno5=\"{17}\", fno6=\"{18}\");
    SeaGap.make_initial_gradv({4} , {5}, fn=\"{13}\", fno=\"gui_tmp/tmp_static_array_s_initial.inp\");
    SeaGap.static_array_mcmcgradv({0}, {2}, [{3}], {4}, {5}, {6}, {7}, gm={19}, dm={20}, ds={21}, rm={22}, rs={23}, nloop={24}, nburn={25},  fn1=\"{8}\", fn2=\"{9}\", fn3=\"{10}\", fn4=\"{11}\", fn5=\"gui_tmp/tmp_static_array_s_initial.inp\", fno0=\"{26}\", fno1=\"{27}\", fno2=\"{28}\", fno3=\"{29}\", fno4=\"{30}\", fno5=\"{31}\", fno6=\"{32}\", fno7=\"{33}\", fno8=\"{34}\", fno9=\"{35}\");
    SeaGap.plot_mcmcres_gradv(nshuffle={36}, fn=\"{28}\", show=false, fno=\"{37}\");
    SeaGap.plot_mcmcparam_gradv(5, nshuffle={36}, fn=\"{27}\", show=false, fno=\"{38}\")' '''
    .format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')

    # lat, dep, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), NPB1, NPB2, NPB3, NPB4, gm=gm, gs=gs, dm=dm, ds=ds, rm=rm, rs=rs, nloop=nloop, nburn=nburn, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, fn5="gui_tmp/tmp_static_array_s_initial.inp", fno0=log_path, fno1=sample_path, fno2=mcmc_path, fno3=position_path, fno4=statistics_path, fno5=acceptance_path, fno6=residual_path, fno7=bspline_path, fno8=gradient_path, fno9=initial_path)

    cont.stop()

    # lat, TR_DEPTH, 0.0,  NPB1, NPB2, path_ANT, path_PXP, path_SSP, path_OBS, "gui_tmp/tmp_static_array_s_log.txt", "gui_tmp/tmp_static_array_s_solve.out", "gui_tmp/tmp_static_array_s_position.out", "gui_tmp/tmp_static_array_s_residual_sdls.out", "gui_tmp/tmp_static_array_s_S-NTD.out", "gui_tmp/tmp_static_array_s_ABIC.out", "gui_tmp/tmp_static_array_s_gradient.out"

    # self.jl.SeaGap.static_array_s(lat, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), 0.0, NPB1, NPB2, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, fno0="gui_tmp/tmp_static_array_s_log.txt",fno1="gui_tmp/tmp_static_array_s_solve.out",fno2="gui_tmp/tmp_static_array_s_position.out",fno3="gui_tmp/tmp_static_array_s_residual_sdls.out",fno4="gui_tmp/tmp_static_array_s_S-NTD.out",fno5="gui_tmp/tmp_static_array_s_ABIC.out",fno6="gui_tmp/tmp_static_array_s_gradient.out")
    # self.jl.SeaGap.make_initial_gradv(NPB1, NPB2, fn="gui_tmp/tmp_static_array_s_solve.out", fno="gui_tmp/tmp_static_array_s_initial.inp")
    # self.jl.SeaGap.static_array_mcmcgradv(lat, dep, juliacall.convert(self.jl.Vector[self.jl.Float64], [TR_DEPTH]), NPB1, NPB2, NPB3, NPB4, gm=gm, gs=gs, dm=dm, ds=ds, rm=rm, rs=rs, nloop=nloop, nburn=nburn, fn1=path_ANT, fn2=path_PXP, fn3=path_SSP, fn4=path_OBS, fn5="gui_tmp/tmp_static_array_s_initial.inp", fno0=log_path, fno1=sample_path, fno2=mcmc_path, fno3=position_path, fno4=statistics_path, fno5=acceptance_path, fno6=residual_path, fno7=bspline_path, fno8=gradient_path, fno9=initial_path)
    #
    # self.jl.SeaGap.plot_mcmcres_gradv(nshuffle=nshuffle, fn=mcmc_path, show=False, fno=resfig_path) #, fno="gui_tmp/test.png"
    #
    # self.jl.SeaGap.plot_mcmcparam_gradv(5, nshuffle=nshuffle, fn=sample_path, show=False, fno=paramfig_path) #, fno="gui_tmp/test.png"

def static_individual_proc(*args, **kwargs):
    client = docker.from_env()
    cont = client.containers.run("githoru/seagap_docker_img", "sleep infinity", auto_remove=True, detach=True, volumes=[os.path.normpath(kwargs["proj_fold"])+":/app"])
    _, stream = cont.exec_run('''julia -e 'using SeaGap;SeaGap.static_individual({0}, [{1}], {2}, fn1=\"{3}\", fn2=\"{4}\", fn3=\"{5}\", fn4=\"{6}\", eps={7}, ITMAX={8}, delta_pos={9}, fno0=\"{10}\", fno1=\"{11}\", fno2=\"{12}\", fno3=\"{13}\", fno4=\"{14}\")' '''.format(*args), stream=True)
    for data in stream:
        print(data.decode(), end='')
    cont.stop()
    # self.buttonBox.setDisabled(False)

