import torch
import torch.nn as nn
# from torch.autograd import Variable

"Autoencoder without seq"
class Autoencoder(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Autoencoder, self).__init__()

        print("AE_Model: Autoencoder")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]

            #encoder layers
            self.e_fc1 = nn.Linear(self.input_size, 512)
            # self.e_fc2 = nn.Linear(512, 512)
            self.e_fc2 = nn.Linear(512, 256)
            self.e_fc3 = nn.Linear(256, 128)
            self.e_fc4 = nn.Linear(128, 64)
            self.e_fc5 = nn.Linear(64, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, 64)
            self.d_fc2 = nn.Linear(64, 128)
            self.d_fc3 = nn.Linear(128, 256)
            self.d_fc4 = nn.Linear(256, 512)
            self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout = nn.Dropout(0.25)
            self.relu    = nn.ReLU()

    def encoder(self, x):
        #non linear encoder
        if not self.linear_ae:
            
            x = self.relu(self.e_fc1(x))
            # x = self.dropout(x)
            x = self.relu(self.e_fc2(x))
            # x = self.dropout(x)
            x = self.relu(self.e_fc3(x))
            # x = self.dropout(x)
            x = self.relu(self.e_fc4(x))
            x = self.e_fc5(x)
            # x = self.relu(self.e_fc6(x))
        
        #linear encoder
        else:
            x = self.e_fc1(x)
            x = self.e_fc2(x)
            x = self.e_fc3(x)
            x = self.e_fc4(x)
            x = self.e_fc5(x)
        
        return x
    
    def decoder(self, x):
        #non linear encoder
        if not self.linear_ae:
            x = self.relu(self.d_fc1(x))
            x = self.relu(self.d_fc2(x))
            # x = self.dropout(x)
            x = self.relu(self.d_fc3(x))
            # x = self.dropout(x)
            x = self.relu(self.d_fc4(x))
            # x = self.dropout(x)
            x = self.d_fc5(x)
        
        #linear encoder
        else:
            x = self.d_fc1(x)
            x = self.d_fc2(x)
            x = self.d_fc3(x)
            x = self.d_fc4(x)
            x = self.d_fc5(x)

        return x

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count

#creates nn network using sequential method
class Autoencoder_sequential(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Autoencoder_sequential, self).__init__()

        print("AE_Model: Autoencoder_sequential")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]

            ## For old models where dropout was not possible
            #non linear autoencoder
            if not self.linear_ae:
                self.encoder = nn.Sequential(
                    nn.Linear(self.input_size, 512),
                    # torch.nn.Dropout(p=0.5, inplace=False)
                    # nn.Tanh(inplace=True),
                    nn.ReLU(),
                    nn.Linear(512, 256),
                    nn.ReLU(),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, self.latent_size)
                )

                self.decoder = nn.Sequential(
                    nn.Linear(self.latent_size, 64),
                    nn.ReLU(),
                    nn.Linear(64, 128),
                    nn.ReLU(),
                    nn.Linear(128, 256),
                    nn.ReLU(),
                    nn.Linear(256, 512),
                    nn.ReLU(),
                    nn.Linear(512, self.input_size)
                )
            
            #linear autoencoder
            else:
                self.encoder = nn.Sequential(
                    nn.Linear(self.input_size, 512),
                    # nn.Tanh(inplace=True),
                    nn.Linear(512, 256),
                    nn.Linear(256, 128),
                    nn.Linear(128, 64),
                    nn.Linear(64, self.latent_size)
                )

                self.decoder = nn.Sequential(
                    nn.Linear(self.latent_size, 64),
                    nn.Linear(64, 128),
                    nn.Linear(128, 256),
                    nn.Linear(256, 512),
                    nn.Linear(512, self.input_size)
                )


            # self.encoder = nn.Sequential(
            #     nn.Linear(input_size, 100),
            #     nn.ReLU(inplace=True),
            #     nn.Linear(100, 100),
            #     nn.ReLU(inplace=True),
            #     nn.Linear(100, latent_size)
            # )

            # self.decoder = nn.Sequential(
            #     nn.Linear(latent_size, 100),
            #     nn.ReLU(inplace=True),
            #     nn.Linear(100, 100),
            #     nn.ReLU(inplace=True),
            #     nn.Linear(100, input_size)
            # )
            
            
            # print('Total number of parameters: {}'.format(self._num_parameters()))

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count

######################################################################
"1D-Convolution Autoencoder"
class Conv1D_Autoencoder(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Conv1D_Autoencoder, self).__init__()

        print("AE_Model: Conv1D_Autoencoder")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]
            self.conv_filter_size = self.args["conv_filter_size"]
            self.statedim    = self.args["statedim"]

            self.num_convlayers = 3


            #encoder layers
            self.e_cc1 = nn.Conv1d(1,16, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc1_bn = nn.BatchNorm1d(16) 
            self.e_cc1_mp = nn.MaxPool1d(kernel_size = self.conv_filter_size, stride=1, padding=int((self.conv_filter_size-1)/2), dilation=1, return_indices=False, ceil_mode=False)
            
            self.e_cc2 = nn.Conv1d(16, 8, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc2_bn = nn.BatchNorm1d(8)
            
            self.e_cc3 = nn.Conv1d(8, 4, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc3_bn = nn.BatchNorm1d(4) 

            e_fc1_fdim = 4*(self.statedim-(self.conv_filter_size-1)*self.num_convlayers)
            self.e_fc1 = nn.Linear(e_fc1_fdim, 256)
            self.e_fc2 = nn.Linear(256,96)
            self.e_fc3 = nn.Linear(96, self.latent_size)
            self.e_fc4 = nn.Linear(self.latent_size, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, self.latent_size)
            self.d_fc2 = nn.Linear(self.latent_size, 96)
            self.d_fc3 = nn.Linear(96, 256)
            self.d_fc4 = nn.Linear(256, e_fc1_fdim)

            self.d_cc1 = torch.nn.ConvTranspose1d(4, 8, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc1_bn = nn.BatchNorm1d(8)
            self.d_cc2 = torch.nn.ConvTranspose1d(8, 16, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc2_bn = nn.BatchNorm1d(16)
            self.d_cc3 = torch.nn.ConvTranspose1d(16, 4, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.d_cc4 = torch.nn.ConvTranspose2d(64, 2, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc3_bn = nn.BatchNorm1d(4)
            self.d_cc4 = torch.nn.ConvTranspose1d(4, 1, 1, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)

            # self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout   = nn.Dropout(p=0.1)
            self.dropout2d = nn.Dropout2d(p=0.8, inplace=True)
            self.af        = nn.ReLU()

    def encoder(self, x):

        #reinitialisiing some parameters for old model analysis -> not part of algo logic
        self.af        = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)

        #non linear encoder
        x = x[...,None,:]
        print("encoder in: ", x.shape)
        x = self.e_cc1_bn(self.e_cc1_mp(self.af(self.e_cc1(x))))
        print("encoder in 2: ", x.shape)
        x = self.e_cc2_bn(self.e_cc1_mp(self.af(self.e_cc2(x))))
        x = self.e_cc3_bn(self.e_cc1_mp(self.af(self.e_cc3(x))))
        # x = self.af(self.e_cc4(x))
        # print("in encoder: ", x.shape)
        x = torch.flatten(x, start_dim = 1)

        x = self.af(self.e_fc1(x))
        # x = self.dropout(x)
        x = self.dropout(self.af(self.e_fc2(x)))
        # x = self.dropout(x)
        x = self.af(self.e_fc3(x))
        x = self.e_fc4(x)
        
        return x.squeeze(dim = -2)
    
    def decoder(self, x):
        self.af = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)

        #non linear decoder
        x = x[...,None,:]    
        x = self.d_fc1(x)
        x = self.af(self.d_fc2(x))
        x = self.af(self.d_fc3(x))
        # x = self.dropout(x)
        x = self.af(self.d_fc4(x))
        # x = self.dropout(x)

        # print("in decoder: ", x.shape)
        firstdim_for_convx = int(x.numel()/(4*(self.statedim-(self.conv_filter_size-1)*self.num_convlayers)))
        x = x.reshape(firstdim_for_convx,4,(self.statedim-(self.conv_filter_size-1)*self.num_convlayers))

        x = self.d_cc1_bn(self.e_cc1_mp(self.af(self.d_cc1(x))))
        x = self.d_cc2_bn(self.e_cc1_mp(self.af(self.d_cc2(x))))
        x = self.af(self.d_cc3(x))
        print("decoder out 2: ", x.shape)
        x = self.d_cc4(x)
        print("decoder out: ", x.shape)

        return x

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count

######################################################################
"2D-Autoencoder"
class Conv2D_Autoencoder(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Conv2D_Autoencoder, self).__init__()

        print("AE_Model: Conv_Autoencoder")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]

            #encoder layers
            self.e_cc1 = nn.Conv2d(2, 64, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.e_cc2 = nn.Conv1d(26, 256, 2, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=None, dtype=None)
            self.e_cc2 = nn.Conv2d(64, 32, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc3 = nn.Conv2d(32, 16, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc4 = nn.Conv2d(16, 8, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)

            self.e_fc1 = nn.Linear(10064, 5000)
            self.e_fc2 = nn.Linear(5000,1000)
            self.e_fc3 = nn.Linear(1000, self.latent_size)
            self.e_fc4 = nn.Linear(self.latent_size, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, self.latent_size)
            self.d_fc2 = nn.Linear(self.latent_size, 1000)
            self.d_fc3 = nn.Linear(1000, 5000)
            self.d_fc4 = nn.Linear(5000, 10064)

            self.d_cc1 = torch.nn.ConvTranspose2d(8, 16, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc2 = torch.nn.ConvTranspose2d(16, 32, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc3 = torch.nn.ConvTranspose2d(32, 64, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc4 = torch.nn.ConvTranspose2d(64, 2, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc5 = torch.nn.ConvTranspose2d(2, 2, 1, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)

            # self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout = nn.Dropout(0.25)
            self.relu    = nn.ReLU()

    def encoder(self, x):
        #non linear encoder
        if not self.linear_ae:
            
            x = self.relu(self.e_cc1(x))
            # x = self.dropout(x)
            x = self.relu(self.e_cc2(x))
            # x = self.dropout(x)
            x = self.relu(self.e_cc3(x))
            # x = self.dropout(x)
            x = self.relu(self.e_cc4(x))
            # print("in encoder: ", x.shape)
            x = torch.flatten(x, start_dim = 1)
            x = self.relu(self.e_fc1(x))
            x = self.relu(self.e_fc2(x))
            x = self.relu(self.e_fc3(x))
            x = self.relu(self.e_fc4(x))


            # x = self.relu(self.e_fc6(x))
        
        #linear encoder
        else:
            x = self.e_fc1(x)
            x = self.e_fc2(x)
            x = self.e_fc3(x)
            x = self.e_fc4(x)
            x = self.e_fc5(x)
        
        return x
    
    def decoder(self, x):
        #non linear encoder
        if not self.linear_ae:
            
            x = self.d_fc1(x)
            x = self.relu(self.d_fc2(x))
            # x = self.dropout(x)
            x = self.relu(self.d_fc3(x))
            # x = self.dropout(x)
            x = self.relu(self.d_fc4(x))
            # x = self.dropout(x)
            
            # print("in decoder: ", x.shape)
            firstdim_for_convx = int(x.numel()/(8*34*37))
            x = x.reshape(firstdim_for_convx,8,34,37)

            x = self.relu(self.d_cc1(x))
            x = self.relu(self.d_cc2(x))
            x = self.relu(self.d_cc3(x))
            x = self.relu(self.d_cc4(x))
            x = self.d_cc5(x)

        #linear encoder
        else:
            x = self.d_fc1(x)
            x = self.d_fc2(x)
            x = self.d_fc3(x)
            x = self.d_fc4(x)
            x = self.d_fc5(x)

        return x

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count
    
######################################################################
"2D-Autoencoder"
class Conv2D_Autoencoder_2(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Conv2D_Autoencoder_2, self).__init__()

        print("AE_Model: Conv_Autoencoder_2")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]
            self.conv_filter_size = self.args["conv_filter_size"]
            self.statedim    = self.args["statedim"]

            self.num_convlayers = 3


            #encoder layers
            self.e_cc1 = nn.Conv2d(self.statedim[-3], 16, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.e_cc2 = nn.Conv1d(26, 256, 2, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=None, dtype=None)
            self.e_cc1_bn = nn.BatchNorm2d(16) 
            self.e_cc2 = nn.Conv2d(16, 8, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc2_bn = nn.BatchNorm2d(8) 
            self.e_cc3 = nn.Conv2d(8, 4, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc3_bn = nn.BatchNorm2d(4) 
            # self.e_cc4 = nn.Conv2d(8, 4, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)

            e_fc1_fdim = 4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)
            self.e_fc1 = nn.Linear(e_fc1_fdim, 1000)
            self.e_fc2 = nn.Linear(1000,800)
            self.e_fc3 = nn.Linear(800, self.latent_size)
            self.e_fc4 = nn.Linear(self.latent_size, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, self.latent_size)
            self.d_fc2 = nn.Linear(self.latent_size, 800)
            self.d_fc3 = nn.Linear(800, 1000)
            self.d_fc4 = nn.Linear(1000, e_fc1_fdim)

            self.d_cc1 = torch.nn.ConvTranspose2d(4, 8, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc1_bn = nn.BatchNorm2d(8)
            self.d_cc2 = torch.nn.ConvTranspose2d(8, 16, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc2_bn = nn.BatchNorm2d(16)
            self.d_cc3 = torch.nn.ConvTranspose2d(16, self.statedim[-3], self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.d_cc4 = torch.nn.ConvTranspose2d(64, 2, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc3_bn = nn.BatchNorm2d(self.statedim[-3])
            self.d_cc4 = torch.nn.ConvTranspose2d(self.statedim[-3], self.statedim[-3], 1, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)

            # self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout   = nn.Dropout(p=0.25)
            self.dropout2d = nn.Dropout2d(p=0.8, inplace=True)
            self.af        = nn.ReLU()

    def encoder(self, x):
        #non linear encoder
        self.af        = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)

        if not self.linear_ae:
            
            x = self.e_cc1_bn(self.af(self.e_cc1(x)))
            x = self.e_cc2_bn(self.af(self.e_cc2(x)))
            x = self.e_cc3_bn(self.af(self.e_cc3(x)))
            # x = self.af(self.e_cc4(x))
            # print("in encoder: ", x.shape)
            x = torch.flatten(x, start_dim = 1)

            x = self.af(self.e_fc1(x))
            x = self.dropout(x)
            x = self.dropout(self.af(self.e_fc2(x)))
            x = self.dropout(x)
            x = self.af(self.e_fc3(x))
            x = self.af(self.e_fc4(x))

            # x = self.af(self.e_fc6(x))
        #linear encoder
        else:
            x = self.e_fc1(x)
            x = self.e_fc2(x)
            x = self.e_fc3(x)
            x = self.e_fc4(x)
            x = self.e_fc5(x)
        
        return x
    
    def decoder(self, x):
        self.af = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)
        #non linear encoder
        if not self.linear_ae:
            
            x = self.d_fc1(x)
            x = self.af(self.d_fc2(x))
            x = self.af(self.d_fc3(x))
            x = self.dropout(x)
            x = self.af(self.d_fc4(x))
            x = self.dropout(x)

            # print("in decoder: ", x.shape)
            firstdim_for_convx = int(x.numel()/(4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)))
            x = x.reshape(firstdim_for_convx,4,self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers,self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)

            x = self.d_cc1_bn(self.af(self.d_cc1(x)))
            x = self.d_cc2_bn(self.af(self.d_cc2(x)))
            x = self.d_cc3_bn(self.af(self.d_cc3(x)))
            # x = self.af(self.d_cc4(x))
            x = self.d_cc4(x)

        #linear encoder
        else:
            x = self.d_fc1(x)
            x = self.d_fc2(x)
            x = self.d_fc3(x)
            x = self.d_fc4(x)
            x = self.d_fc5(x)

        return x

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count

######################################################################
"2D-Autoencoder"
class Conv2D_Autoencoder_3(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Conv2D_Autoencoder_3, self).__init__()

        print("AE_Model: Conv_Autoencoder_3")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]
            self.conv_filter_size = self.args["conv_filter_size"]
            self.statedim    = self.args["statedim"]

            self.num_convlayers = 3

            #encoder layers
            self.e_cc1 = nn.Conv2d(self.statedim[-3], 16, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.e_cc2 = nn.Conv1d(26, 256, 2, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=None, dtype=None)
            self.e_cc1_bn = nn.BatchNorm2d(16) 
            self.e_cc1_mp = nn.MaxPool2d(kernel_size = self.conv_filter_size, stride=1, padding=1, dilation=1, return_indices=False, ceil_mode=False)
            
            self.e_cc2 = nn.Conv2d(16, 8, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc2_bn = nn.BatchNorm2d(8)
            
            self.e_cc3 = nn.Conv2d(8, 4, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc3_bn = nn.BatchNorm2d(4) 
            # self.e_cc4 = nn.Conv2d(8, 4, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)

            e_fc1_fdim = 4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)
            self.e_fc1 = nn.Linear(e_fc1_fdim, 1000)
            self.e_fc2 = nn.Linear(1000,800)
            self.e_fc3 = nn.Linear(800, self.latent_size)
            self.e_fc4 = nn.Linear(self.latent_size, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, self.latent_size)
            self.d_fc2 = nn.Linear(self.latent_size, 800)
            self.d_fc3 = nn.Linear(800, 1000)
            self.d_fc4 = nn.Linear(1000, e_fc1_fdim)

            self.d_cc1 = torch.nn.ConvTranspose2d(4, 8, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc1_bn = nn.BatchNorm2d(8)
            self.d_cc2 = torch.nn.ConvTranspose2d(8, 16, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc2_bn = nn.BatchNorm2d(16)
            self.d_cc3 = torch.nn.ConvTranspose2d(16, self.statedim[-3], self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.d_cc4 = torch.nn.ConvTranspose2d(64, 2, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc3_bn = nn.BatchNorm2d(self.statedim[-3])
            self.d_cc4 = torch.nn.ConvTranspose2d(self.statedim[-3], self.statedim[-3], 1, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)

            # self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout   = nn.Dropout(p=0.25)
            self.dropout2d = nn.Dropout2d(p=0.8, inplace=True)
            self.af        = nn.ReLU()

    def encoder(self, x):
        #non linear encoder
        self.af        = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)

        if not self.linear_ae:
            
            x = self.e_cc1_bn(self.e_cc1_mp(self.af(self.e_cc1(x))))
            x = self.e_cc2_bn(self.e_cc1_mp(self.af(self.e_cc2(x))))
            x = self.e_cc3_bn(self.e_cc1_mp(self.af(self.e_cc3(x))))
            # x = self.af(self.e_cc4(x))
            # print("in encoder: ", x.shape)
            x = torch.flatten(x, start_dim = 1)

            x = self.af(self.e_fc1(x))
            x = self.dropout(x)
            x = self.dropout(self.af(self.e_fc2(x)))
            x = self.dropout(x)
            x = self.af(self.e_fc3(x))
            x = self.e_fc4(x)

        #linear encoder
        else:
            x = self.e_fc1(x)
            x = self.e_fc2(x)
            x = self.e_fc3(x)
            x = self.e_fc4(x)
            x = self.e_fc5(x)
        
        return x
    
    def decoder(self, x):
        self.af = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)
        #non linear encoder
        if not self.linear_ae:
            
            x = self.d_fc1(x)
            x = self.af(self.d_fc2(x))
            x = self.af(self.d_fc3(x))
            x = self.dropout(x)
            x = self.af(self.d_fc4(x))
            x = self.dropout(x)

            # print("in decoder: ", x.shape)
            firstdim_for_convx = int(x.numel()/(4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)))
            x = x.reshape(firstdim_for_convx,4,self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers,self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)

            x = self.d_cc1_bn(self.e_cc1_mp(self.af(self.d_cc1(x))))
            x = self.d_cc2_bn(self.e_cc1_mp(self.af(self.d_cc2(x))))
            x = self.d_cc3_bn(self.e_cc1_mp(self.af(self.d_cc3(x))))
            # x = self.af(self.d_cc4(x))
            x = self.d_cc4(x)

        #linear encoder
        else:
            x = self.d_fc1(x)
            x = self.d_fc2(x)
            x = self.d_fc3(x)
            x = self.d_fc4(x)
            x = self.d_fc5(x)

        return x

    def forward(self, Phi_n):
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count

"2D-Autoencoder"
class Conv2D_Autoencoder_3_stn(nn.Module):

    def __init__(self, args, model_eval = False):
        super(Conv2D_Autoencoder_3_stn, self).__init__()

        print("AE_Model: Conv_Autoencoder_3_stn")

        self.args = args

        if not model_eval:
            self.input_size  = self.args["statedim"] 
            self.latent_size = self.args["num_obs"] 
            self.linear_ae   = self.args["linear_autoencoder"]
            self.conv_filter_size = self.args["conv_filter_size"]
            self.statedim    = self.args["statedim"]
            

            self.num_convlayers = 3

            #encoder layers
            self.e_cc1 = nn.Conv2d(self.statedim[-3], 16, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.e_cc2 = nn.Conv1d(26, 256, 2, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=None, dtype=None)
            self.e_cc1_bn = nn.BatchNorm2d(16) 
            self.e_cc1_mp = nn.MaxPool2d(kernel_size = self.conv_filter_size, stride=1, padding=1, dilation=1, return_indices=False, ceil_mode=False)
            
            self.e_cc2 = nn.Conv2d(16, 8, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc2_bn = nn.BatchNorm2d(8)
            
            self.e_cc3 = nn.Conv2d(8, 4, self.conv_filter_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.e_cc3_bn = nn.BatchNorm2d(4) 
            # self.e_cc4 = nn.Conv2d(8, 4, 5, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=self.args["device"], dtype=None)

            e_fc1_fdim = 4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)
            self.e_fc1 = nn.Linear(e_fc1_fdim, 1000)
            self.e_fc2 = nn.Linear(1000,800)
            self.e_fc3 = nn.Linear(800, self.latent_size)
            self.e_fc4 = nn.Linear(self.latent_size, self.latent_size)

            #decoder layers
            self.d_fc1 = nn.Linear(self.latent_size, self.latent_size)
            self.d_fc2 = nn.Linear(self.latent_size, 800)
            self.d_fc3 = nn.Linear(800, 1000)
            self.d_fc4 = nn.Linear(1000, e_fc1_fdim)

            self.d_cc1 = torch.nn.ConvTranspose2d(4, 8, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc1_bn = nn.BatchNorm2d(8)
            self.d_cc2 = torch.nn.ConvTranspose2d(8, 16, self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc2_bn = nn.BatchNorm2d(16)
            self.d_cc3 = torch.nn.ConvTranspose2d(16, self.statedim[-3], self.conv_filter_size, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            # self.d_cc4 = torch.nn.ConvTranspose2d(64, 2, 5, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)
            self.d_cc3_bn = nn.BatchNorm2d(self.statedim[-3])
            self.d_cc4 = torch.nn.ConvTranspose2d(self.statedim[-3], self.statedim[-3], 1, stride=1, padding=0, output_padding=0, groups=1, bias=True, dilation=1, padding_mode='zeros', device=self.args["device"], dtype=None)

            # self.d_fc5 = nn.Linear(512, self.input_size)
            # self.d_fc6 = nn.Linear(512, input_size)

            #reg layers
            self.dropout   = nn.Dropout(p=0.25)
            self.dropout2d = nn.Dropout2d(p=0.8, inplace=True)
            self.af        = nn.ReLU()

            #attention Tranformer layer
            # Spatial transformer localization-network
            self.localization = nn.Sequential(
                nn.Conv2d(2, 8, kernel_size=7),
                nn.MaxPool2d(2, stride=2),
                nn.ReLU(True),
                nn.Conv2d(8, 10, kernel_size=5),
                nn.MaxPool2d(2, stride=2),
                nn.ReLU(True)
            )

            # Regressor for the 3 * 2 affine matrix
            self.fc_loc = nn.Sequential(
                # nn.Linear(10 * 2 * 6, 32),
                nn.Linear(10 * 9 * 16, 32),
                nn.ReLU(True),
                nn.Linear(32, 3 * 2)
            )

            # Initialize the weights/bias with identity transformation
            self.fc_loc[2].weight.data.zero_()
            self.fc_loc[2].bias.data.copy_(torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float))
    
    # Spatial transformer network forward function
    def stn(self, x):
        xs = self.localization(x)
        # print(xs.shape)

        # xs = xs.view(-1, 10 * 2 * 6)
        xs = xs.view(-1, 10 * 9 * 16)
        theta = self.fc_loc(xs)
        theta = theta.view(-1, 2, 3)

        grid = nn.functional.affine_grid(theta, x.size(), align_corners = True)
        x    = nn.functional.grid_sample(x, grid, align_corners = True)

        return x

    def encoder(self, x):
        #non linear encoder
        self.af        = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)

        if not self.linear_ae:
            
            x = self.e_cc1_bn(self.e_cc1_mp(self.af(self.e_cc1(x))))
            x = self.e_cc2_bn(self.e_cc1_mp(self.af(self.e_cc2(x))))
            x = self.e_cc3_bn(self.e_cc1_mp(self.af(self.e_cc3(x))))
            # x = self.af(self.e_cc4(x))
            # print("in encoder: ", x.shape)
            x = torch.flatten(x, start_dim = 1)

            x = self.af(self.e_fc1(x))
            x = self.dropout(x)
            x = self.dropout(self.af(self.e_fc2(x)))
            x = self.dropout(x)
            x = self.af(self.e_fc3(x))
            x = self.e_fc4(x)

        #linear encoder
        else:
            x = self.e_fc1(x)
            x = self.e_fc2(x)
            x = self.e_fc3(x)
            x = self.e_fc4(x)
            x = self.e_fc5(x)
        
        return x
    
    def decoder(self, x):
        self.af = nn.ReLU()
        self.num_convlayers = 3
        self.dropout   = nn.Dropout(p=0.25)
        #non linear encoder
        if not self.linear_ae:
            
            x = self.d_fc1(x)
            x = self.af(self.d_fc2(x))
            x = self.af(self.d_fc3(x))
            x = self.dropout(x)
            x = self.af(self.d_fc4(x))
            x = self.dropout(x)

            # print("in decoder: ", x.shape)
            firstdim_for_convx = int(x.numel()/(4*(self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers)*(self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)))
            x = x.reshape(firstdim_for_convx,4,self.statedim[1]-(self.conv_filter_size-1)*self.num_convlayers,self.statedim[2]-(self.conv_filter_size-1)*self.num_convlayers)

            x = self.d_cc1_bn(self.e_cc1_mp(self.af(self.d_cc1(x))))
            x = self.d_cc2_bn(self.e_cc1_mp(self.af(self.d_cc2(x))))
            x = self.d_cc3_bn(self.e_cc1_mp(self.af(self.d_cc3(x))))
            # x = self.af(self.d_cc4(x))
            x = self.d_cc4(x)

        #linear encoder
        else:
            x = self.d_fc1(x)
            x = self.d_fc2(x)
            x = self.d_fc3(x)
            x = self.d_fc4(x)
            x = self.d_fc5(x)

        return x

    def forward(self, Phi_n):

        Phi_n     = self.stn(Phi_n)  # transformation before paasing to encoder
        x_n       = self.encoder(Phi_n)
        Phi_n_hat = self.decoder(x_n)

        return x_n, Phi_n_hat

    def recover(self, x_n):
        Phi_n_hat = self.decoder(x_n)
        return Phi_n_hat

    def _num_parameters(self):
        count = 0
        for name, param in self.named_parameters():
            # print(name, param.numel())
            count += param.numel()
        return count