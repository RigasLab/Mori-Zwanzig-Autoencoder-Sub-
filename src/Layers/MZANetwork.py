import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from src.PreProc_Data.DataProc import SequenceDataset


class MZANetwork(nn.Module):
    def __init__(self, exp_args : dict, 
                       autoencoder : object,
                       koopman : object,
                       seqmodel  : object):
        super(MZANetwork, self).__init__()
        
        
        self.args        = exp_args
        self.autoencoder = autoencoder(input_size = self.args["statedim"], latent_size = self.args["num_obs"], linear_ae = self.args["linear_autoencoder"])
        self.koopman     = koopman(latent_size = self.args["num_obs"], device = self.args["device"], stable_koopman_init = self.args["stable_koopman_init"])
        if not self.args["deactivate_seqmodel"] or (self.args["nepoch_actseqmodel"] != 0):
            self.seqmodel    = seqmodel(N = self.args["num_obs"], input_size = self.args["num_obs"], 
                                    hidden_size = self.args["num_hidden_units"], num_layers = self.args["num_layers"], 
                                    seq_length = self.args["seq_len"], device = self.args["device"]).to(self.args["device"])

            if (self.args["nepoch_actseqmodel"] != 0):
                for param in self.seqmodel.parameters():
                    param.requires_grad = False
                

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            print(name, param.numel())
            count += param.numel()
        return count


    def get_observables(self, Phi):

        """
        Computes observables using encoder
        Input
        -----
        Phi : [time, statedim] State variables
        
        Returns
        -------
        x : [time, obsdim] Obervables
        """
        
        x = self.autoencoder.encoder(Phi)
        return x
    
    def create_obs_dataset(self, Phi, shuffle):

        """
        Creates sequence dataset for the observables along with the coresponding state variables
        Input
        -----
        Phi : [time, statedim] State variables
        x   : [time, obsdim] Obervables
        shuffle : [Bool] Shuffle the dataloader or not
        
        Returns
        -------
        Dataloader and Dataset
        """

        x = self.get_observables(Phi)

        dataset = SequenceDataset(Phi, x, self.args.device, sequence_length=self.args.seq_len)
        dataloader = DataLoader(dataset, batch_size = self.args.batch_size, shuffle = shuffle)

        return dataloader, dataset

    
    def save_model(self, exp_dir, exp_name):

        '''
        Saves the models to the given exp_dir and exp_name
        '''

        torch.save(self.seqmodel, exp_dir+'/'+exp_name+"/seqmodel_"+exp_name)
        print("saved the seqmodel")
        torch.save(self.autoencoder, exp_dir+'/'+exp_name+"/autoencoder_"+exp_name)
        print("saved the autoencoder model")


        

        


