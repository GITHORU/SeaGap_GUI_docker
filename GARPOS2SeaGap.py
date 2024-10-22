import pandas as pd
import os

def GARPOS2SeaGap(path_obs, path_svp, path_ini, path_pxp_o, path_obs_o, path_ssp_o, path_ant_o, split_sets=True):
    with open(path_obs, 'r') as file :
        obs_df = pd.read_csv(file, skiprows=1, index_col=0)


    with open(path_ini, 'r') as file :
        with open(path_ant_o, "w") as file_o :
            line = file.readline()
            flag = True
            l_mount = []
            l_pos = []
            while line and flag :
                if "[Model-parameter]" in line :
                    line = file.readline()
                    line = file.readline()
                    while len(line.split("=")) == 2 and not "dCentPos" in line:
                        mount = line.split("=")[0].split("_")[0].strip()
                        val_list = [float(val) for val in line.split("=")[1].split()]
                        l_mount.append(mount)
                        l_pos.append(val_list[:6])
                        line = file.readline()
                    flag = False
                line = file.readline()
            flag = True
            while line and flag :
                if "ATDoffset" in line :
                    val_list = [float(val) for val in line.split("=")[1].split()]
                    file_o.write(str(val_list[1])+" "+str(val_list[0])+" "+str(-val_list[2])+"\n")
                    # val_list[2] = -val_list[2]
                    # for val in val_list[:3]:
                    #     file_o.write(str(val)+" ")
                    # file_o.write("\n")
                    flag = False
                line = file.readline()

    with open(path_svp, 'r') as file:
        with open(path_ssp_o, 'w') as file_o :
            line = file.readline()
            line = file.readline()
            while line :
                d, s = line.split(",")
                file_o.write(d+" "+s)
                line = file.readline()

    with open(path_pxp_o, "w") as file :
        for pos in l_pos :
            chaine = ""
            for val in pos :
                chaine = chaine + " " + str(val)
            chaine = chaine[1:] + "\n"
            file.write(chaine)

    if not split_sets :

        with open(path_obs_o, "w") as file :
            chaine = ""
            session = 1
            l_current_tr = []
            for index, row in obs_df.iterrows():
                mount_index = l_mount.index(row["MT"])+1
                if mount_index in l_current_tr :
                    session += 1
                    l_current_tr = [mount_index]
                else :
                    l_current_tr.append(mount_index)
                chaine = chaine + str(mount_index) #str(row["MT"])
                chaine = chaine + " " + str(row["TT"])
                chaine = chaine + " " + str(row["ST"])
                chaine = chaine + " " + str(row["ant_e0"])
                chaine = chaine + " " + str(row["ant_n0"])
                chaine = chaine + " " + str(row["ant_u0"])
                chaine = chaine + " " + str(row["head0"])
                chaine = chaine + " " + str(row["pitch0"])
                chaine = chaine + " " + str(row["roll0"])
                chaine = chaine + " " + str(row["RT"])
                chaine = chaine + " " + str(row["ant_e1"])
                chaine = chaine + " " + str(row["ant_n1"])
                chaine = chaine + " " + str(row["ant_u1"])
                chaine = chaine + " " + str(row["head1"])
                chaine = chaine + " " + str(row["pitch1"])
                chaine = chaine + " " + str(row["roll1"])
                chaine = chaine + " " + str(session)
                chaine = chaine + " 1\n"
                file.write(chaine)
                chaine = ""

    else :
        set = None
        file = None
        for index, row in obs_df.iterrows():
            if set == None or row["SET"] != set:
                set = row["SET"]
                if file != None :
                    file.close()
                A, B = os.path.splitext(path_obs_o)
                file = open(A+"_"+set+B, 'w')
            chaine = ""
            session = 1
            l_current_tr = []
            mount_index = l_mount.index(row["MT"])+1
            if mount_index in l_current_tr :
                session += 1
                l_current_tr = [mount_index]
            else :
                l_current_tr.append(mount_index)
            chaine = chaine + str(mount_index) #str(row["MT"])
            chaine = chaine + " " + str(row["TT"])
            chaine = chaine + " " + str(row["ST"])
            chaine = chaine + " " + str(row["ant_e0"])
            chaine = chaine + " " + str(row["ant_n0"])
            chaine = chaine + " " + str(row["ant_u0"])
            chaine = chaine + " " + str(row["head0"])
            chaine = chaine + " " + str(row["pitch0"])
            chaine = chaine + " " + str(row["roll0"])
            chaine = chaine + " " + str(row["RT"])
            chaine = chaine + " " + str(row["ant_e1"])
            chaine = chaine + " " + str(row["ant_n1"])
            chaine = chaine + " " + str(row["ant_u1"])
            chaine = chaine + " " + str(row["head1"])
            chaine = chaine + " " + str(row["pitch1"])
            chaine = chaine + " " + str(row["roll1"])
            chaine = chaine + " " + str(session)
            chaine = chaine + " 1\n"
            file.write(chaine)
            chaine = ""
        file.close()


if __name__ == '__main__':
    path_obs = "GARPOS_data/GNSS-A_data_200820/obsdata/MYGI/MYGI.1103.meiyo_m4-obs.csv"
    path_svp = "GARPOS_data/GNSS-A_data_200820/obsdata/MYGI/MYGI.1103.meiyo_m4-svp.csv"
    path_ini = "GARPOS_data/GNSS-A_data_200820/initcfg/MYGI/MYGI.1103.meiyo_m4-initcfg.ini"

    path_pxp_o = "GARPOS_data/output/pxp-ini.inp"
    path_obs_o = "GARPOS_data/output/obsdata.inp"
    path_ssp_o = "GARPOS_data/output/ss_prof.inp"
    path_ant_o = "GARPOS_data/output/tr-ant.inp"

    GARPOS2SeaGap(path_obs, path_svp, path_ini, path_pxp_o, path_obs_o, path_ssp_o, path_ant_o)