import torch
import csv, pickle, copy
# from torch.utils.data import DataLoader

from src.Layers.MZANetwork import MZANetwork

from src.Train_Methods.Train_Methodology import Train_Methodology
from src.PreProc_Data.DynSystem_Data import DynSystem_Data
from torch.optim.lr_scheduler import StepLR

import matplotlib.pyplot as plt
import pandas as pd

# from utils.train_test import train_model, test_model, predict
from src.utils.make_dir import mkdirs
# from torch.utils.tensorboard import SummaryWriter
torch.manual_seed(99)


class MZA_Experiment(DynSystem_Data, Train_Methodology):

    def __init__(self,args):

        #Device parameters
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps") 
        else:
            self.device = torch.device("cpu")
        
        #Data Parameters
        if str(type(args)) != "<class 'dict'>":

            self.dynsys      = args.dynsys
            self.train_size  = args.train_size
            self.batch_size  = args.bs
            self.ntransients = args.ntransients
            self.seq_len     = args.seq_len
            self.time_sample = args.time_sample
            self.nenddata    = args.nenddata
            self.np          = args.noise_p
            self.noisecolor  = args.noisecolor

            #Autoncoder Parameters          
            self.autoencoder_model  = args.AE_Model 
            self.num_obs            = args.num_obs
            self.linear_autoencoder = args.linear_autoencoder 

            #Koopman Parameters
            self.koop_model          = args.Koop_Model
            self.stable_koopman_init = args.stable_koopman_init

            #RNN Parameters
            self.seq_model           = args.Seq_Model
            self.deactivate_seqmodel = args.deactivate_seqmodel
            self.num_layers          = args.nlayers
            self.num_hidden_units    = args.nhu
            self.seq_model_weight    = args.seq_model_weight

            #Model Training # Model Hyper-parameters
            self.learning_rate          = args.lr      
            self.deactivate_lrscheduler = args.deactivate_lrscheduler        
            self.nepochs                = args.nepochs
            self.norm_input             = args.norm_input         #if input should be normalised
            # self.npredsteps         = args.npredsteps
            self.nepoch_actseqmodel     = args.nepoch_actseqmodel
            self.pred_horizon           = args.pred_horizon
            self.lambda_ResL            = args.lambda_ResL

            #Directory Parameters
            self.nsave         = args.nsave                 #after how many epochs to save
            self.info          = args.info                  #extra info in the saved driectory name
            self.exp_dir       = args.exp_dir
            self.exp_name      = "sl{sl}_nhu{nhu}_numobs{numobs}_bs{bs}_{info}".format(sl = args.seq_len, nhu = args.nhu, numobs = args.num_obs, bs=args.bs, info=args.info)
            self.data_dir      = args.data_dir
            self.no_save_model = args.no_save_model
            self.load_epoch    = args.load_epoch
            if self.load_epoch != 0:
                self.exp_name = args.load_exp_name

            self.args = args

           
        
        else:
            for k, v in args.items():
                setattr(self, k, v)
        
        #printing out important information
        print("########## Imp Info ##########")
        print("System: ", self.dynsys)
        if self.deactivate_seqmodel:
            print("Training without Seqmodel")
        
        if self.stable_koopman_init:
            print("Initializing Stable Koopman")
        
        if self.linear_autoencoder:
            print("Using Linear Autoencoder")
        else:
            print("Using Non-Linear Autoencoder")
        
        #emptying gpu cache memory
        torch.cuda.empty_cache()

    def make_directories(self):
        '''
        Makes Experiment Directory
        '''
        directories = [self.exp_dir,
                    self.exp_dir + '/' + self.exp_name,
                    self.exp_dir + '/' + self.exp_name + "/model_weights",
                    self.exp_dir + '/' + self.exp_name + "/out_log",
                    ]
        mkdirs(directories)
    
    
    def log_data(self, load_model = False):

        # Logging Data
        # self.metrics = ["epoch","Train_Loss","Train_ObsEvo_Loss","Train_Autoencoder_Loss","Train_StateEvo_Loss"\
        #                        ,"Test_Loss","Test_ObsEvo_Loss","Test_Autoencoder_Loss","Test_StateEvo_Loss"\
        #                        ,"Train_koop_ptg", "Train_seqmodel_ptg"\
        #                        ,"Test_koop_ptg", "Test_seqmodel_ptg"]

        self.metrics = ["epoch","Train_Loss","Train_KoopEvo_Loss","Train_Residual_Loss","Train_Autoencoder_Loss","Train_StateEvo_Loss"\
                               ,"Test_Loss","Test_KoopEvo_Loss", "Test_Residual_Loss","Test_Autoencoder_Loss","Test_StateEvo_Loss"\
                               ,"Train_koop_ptg", "Train_seqmodel_ptg"\
                               ,"Test_koop_ptg", "Test_seqmodel_ptg"]

        if load_model:
            self.logf = open(self.exp_dir + '/' + self.exp_name + "/out_log/log", "a")
            self.log = csv.DictWriter(self.logf, self.metrics)

        else:
            self.logf = open(self.exp_dir + '/' + self.exp_name + "/out_log/log", "w")
            self.log = csv.DictWriter(self.logf, self.metrics)
            self.log.writeheader()

        print("Logger Initialised")

    def save_args(self):

        #saving args
        with open(self.exp_dir+'/'+self.exp_name+"/args", 'wb') as f:
            args_dict = copy.deepcopy(self.__dict__)

            #deleting some high memory args
            print(args_dict.keys())
            del args_dict['lp_data']
            del args_dict['train_data']
            del args_dict['test_data']
            del args_dict['train_dataset']
            del args_dict['test_dataset']
            del args_dict['train_dataloader']
            del args_dict['test_dataloader']
            # #adding data_args
            # args_dict["data_args"] = data_args
            pickle.dump(args_dict, f)
            print("Saved Args")

    

    def main_train(self, load_model = False):

        #Making Experiment Directory
        self.make_directories()

        #Loading and visualising data
        print("########## LOADING DATASET ##########")
        print("Data Dir: ", self.data_dir)
        self.load_and_preproc_data()

        # #Creating Statevariable Dataset
        self.create_dataset()

        #Creating Model
        print("########## SETTING UP MODEL ##########")
        if not load_model:
            self.model = MZANetwork(self.__dict__).to(self.device)
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr = self.learning_rate, weight_decay=1e-5)
            # print(self.model.parameters)
        
        if not self.deactivate_lrscheduler:
            self.scheduler = StepLR(self.optimizer, 
                    step_size = 20, # Period of learning rate decay
                    gamma = 0.3) # Multiplicative factor of learning rate decay
        # writer = SummaryWriter(exp_dir+'/'+exp_name+'/'+'log/') #Tensorboard writer

        if not load_model:
            #Saving Initial Model state
            if self.no_save_model:
                torch.save({
                    'epoch':-1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict':self.optimizer.state_dict()
                    }, self.exp_dir+'/'+self.exp_name+'/'+self.exp_name)
                
                # torch.save(self.model, self.exp_dir+'/'+self.exp_name+'/'+self.exp_name)

            #saving args
            self.save_args()
        
        if load_model:
            print("AE Model: ", self.autoencoder_model)
            print("Seq Model: ", self.seq_model)
            print("Koop Model: ", self.koop_model)
            
        # Initiating Data Logger
        self.log_data(load_model)

        #Training Model
        self.training_loop()

        #Saving Model
        if self.no_save_model:
            # torch.save(self.model, self.exp_dir+'/'+self.exp_name+'/'+self.exp_name)
            print("model saved in "+ self.exp_dir+'/'+self.exp_name+'/'+self.exp_name)
    
    def plot_learning_curves(self):

        df = pd.read_csv(self.exp_dir+'/'+self.exp_name+"/out_log/log")

        min_trainloss = df.loc[df['Train_Loss'].idxmin(), 'epoch']
        # print("Epoch with Minimum train_error: ", min_trainloss)

        #Total Loss
        plt.figure()
        plt.semilogy(df['epoch'],df['Train_Loss'], label="Train Loss")
        plt.semilogy(df['epoch'], df['Test_Loss'], label="Test Loss")
        plt.legend()
        plt.xlabel("Epochs")
        plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/TotalLoss.png", dpi = 256, facecolor = 'w', bbox_inches='tight')
        plt.close()

        # #Observable Evolution Loss
        # plt.figure()
        # plt.semilogy(df['epoch'],df['Train_ObsEvo_Loss'], label="Train Observable Evolution Loss")
        # plt.semilogy(df['epoch'], df['Test_ObsEvo_Loss'], label="Test Observable Evolution Loss")
        # plt.legend()
        # plt.xlabel("Epochs")
        # plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/ObservableLoss.png", dpi = 256, facecolor = 'w', bbox_inches='tight')

        #KoopEvo Loss
        plt.figure()
        plt.semilogy(df['epoch'],df['Train_KoopEvo_Loss'], label="Train KoopEvo Loss")
        plt.semilogy(df['epoch'], df['Test_KoopEvo_Loss'], label="Test KoopEvo Loss")
        plt.legend()
        plt.xlabel("Epochs")
        plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/KoopEvo.png", dpi = 256, facecolor = 'w', bbox_inches='tight')
        plt.close()

        #Residual Loss
        plt.figure()
        plt.semilogy(df['epoch'],df['Train_Residual_Loss'], label="Train Residual Loss")
        plt.semilogy(df['epoch'], df['Test_Residual_Loss'], label="Test Residual Loss")
        plt.legend()
        plt.xlabel("Epochs")
        plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/ResidualLoss.png", dpi = 256, facecolor = 'w', bbox_inches='tight')
        plt.close()


        #Autoencoder Loss
        plt.figure()
        plt.semilogy(df['epoch'],df['Train_Autoencoder_Loss'], label="Train Autoencoder Loss")
        plt.semilogy(df['epoch'], df['Test_Autoencoder_Loss'], label="Test Autoencoder Loss")
        plt.legend()
        plt.xlabel("Epochs")
        plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/AutoencoderLoss.png", dpi = 256, facecolor = 'w', bbox_inches='tight')
        plt.close()

        #State Loss
        plt.figure()
        plt.semilogy(df['epoch'],df['Train_StateEvo_Loss'], label="Train State Evolution Loss")
        plt.semilogy(df['epoch'], df['Test_StateEvo_Loss'], label="Test State Evolution Loss")
        plt.legend()
        plt.xlabel("Epochs")
        plt.savefig(self.exp_dir+'/'+self.exp_name+"/out_log/StateLoss.png", dpi = 256, facecolor = 'w', bbox_inches='tight')
        plt.close()



    def test(self, load_model = False):
        import numpy as np
        import matplotlib.image as mpimg
        #Loading and visualising data
        print("########## LOADING DATASET ##########")
        print("Data Dir: ", self.data_dir)
        self.load_and_preproc_data()

        plt.figure()
        print
        plt.plot(self.lp_data_without_noise[0,:500,0], label = "normal data")
        plt.plot(self.lp_data[0,:500,1], label = "noise data")
        plt.legend()
        plt.savefig(f"test/noise_images/noise_test_np{self.np}_color{self.noisecolor}.png")

        def plot_spectrum(s, beta):
            f = np.fft.rfftfreq(s.shape[-1])
            spec = np.linalg.norm(np.fft.rfft(s, axis = -1), axis = 1).squeeze()
            data = np.stack((f,spec), axis = 0)

            np.save(f"test/noise_images/data_np{self.np}_color{self.noisecolor}", data)
            print(data.shape)
            
            return plt.loglog(f, spec, label = f"beta: {beta}")[0]

        plt.figure()
        # loaded_plot = mpimg.imread('test/noise_images/initial_plot.png')
        # plt.imshow(loaded_plot)  # Display the loaded plot
        plot_spectrum(self.lp_data,self.noisecolor)
        print("lpshape: ", self.lp_data.shape)
        plt.legend()

        

        plt.savefig(f"test/noise_images/spectrum_noise_test_np{self.np}_color{self.noisecolor}.png")
        # plt.savefig("test/noise_images/initial_plot.png")