from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


def affine_bn_relu_forward(x , w , b, gamma, beta, bn_param):
    a, fc_cache = affine_forward(x, w, b)
    bn, bn_cache = batchnorm_forward(a, gamma, beta, bn_param)
    out, relu_cache = relu_forward(bn)
    cache = (fc_cache, bn_cache, relu_cache)
    return out, cache

def affine_bn_relu_backward(dout, cache):
    fc_cache, bn_cache, relu_cache = cache
    dbn = relu_backward(dout, relu_cache)
    da, dgamma, dbeta =  batchnorm_backward_alt(dbn, bn_cache)
    dx, dw, db = affine_backward(da, fc_cache)
    return dx, dw, db, dgamma, dbeta

class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - dropout: Scalar between 0 and 1 giving dropout strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian with standard deviation equal to   #
        # weight_scale, and biases should be initialized to zero. All weights and  #
        # biases should be stored in the dictionary self.params, with first layer  #
        # weights and biases using the keys 'W1' and 'b1' and second layer weights #
        # and biases using the keys 'W2' and 'b2'.                                 #
        ############################################################################
        self.params['W1'] = weight_scale * np.random.randn(input_dim, hidden_dim)
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['W2'] = weight_scale * np.random.randn(hidden_dim, num_classes)
        self.params['b2'] = np.zeros(num_classes)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        # pass
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        N = X.shape[0]
        reg = self.reg

        hidden_layer = np.maximum(0,np.dot(X.reshape(N,-1),W1) + b1)   #(N,D) * (D,H) = (N,H)   b1 = (H,)
        scores = np.dot(hidden_layer,W2) + b2  #scores = (N,C)  hidden_layer = (N,H), W2 = (H,C) b2=(C,)
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # pass
        #compute the loss:
        shift_scores = scores - np.max(scores,axis = 1).reshape(-1,1)
        prob = np.exp(shift_scores) / (np.sum(np.exp(shift_scores),axis=1).reshape(-1,1))
        loss = -np.sum(np.log(prob[np.arange(N),list(y)])) / N + 0.5 * reg * (np.sum(W1 * W1) + np.sum(W2 * W2))

        #compute the grads:
        dscore = np.copy(prob)
        dscore[np.arange(N),list(y)] += -1
        grads['b2'] = np.sum(dscore,axis = 0) / N   #db2 = (H,)
    
        grads['W2'] = np.dot(hidden_layer.T,dscore)   #dW2 = (H,C)
        grads['W2'] = grads['W2'] / N + reg * W2  

        dh = np.dot(dscore,W2.T) / N
        dReLu = (hidden_layer > 0) * dh
        grads['b1'] = np.sum(dReLu, axis = 0)
        grads['W1'] = np.dot(X.reshape(N,-1).T,dReLu) + reg * W1
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0, use_batchnorm=False, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
          the network should not use dropout at all.
        - use_batchnorm: Whether or not the network should use batch normalization.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.use_batchnorm = use_batchnorm
        self.use_dropout = dropout > 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution with standard deviation equal to  #
        # weight_scale and biases should be initialized to zero.                   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to one and shift      #
        # parameters should be initialized to zero.                                #
        ############################################################################
        # pass
        
        #attention2: batch normalization, need to know what it means.
        current_layer_size = input_dim
        for i in range(len(hidden_dims)):
          hd = hidden_dims[i]
          self.params['W'+str(i+1)] = weight_scale * np.random.randn(current_layer_size, hd)
          self.params['b'+str(i+1)] = np.zeros(hd)
          if self.use_batchnorm:
            self.params['gamma' + str(i+1)] = np.ones(hd)
            self.params['beta' + str(i+1)] = np.zeros(hd)
          current_layer_size = hd

        #attention1: i start from 0, so need to initialize the last FC-layer.
        self.params['W'+str(self.num_layers)] = weight_scale * np.random.randn(current_layer_size, num_classes)
        self.params['b'+str(self.num_layers)] = np.zeros(num_classes)

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.use_batchnorm:
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        # print('----begin loss function----')
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.use_batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode

        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        # pass
        fw_cache = {}
        dp_cache = {}
        layer_input = X
        # print('----begin forward----')
        # print('----num_layers:',self.num_layers)
        for i in range(self.num_layers-1):
          # print('----at',i,'layer----')
          # print('input_layer.shape:',layer_input.shape)
          if self.use_batchnorm:
            # print('---- in forward, use batchnorm,affine_bn_relu_forward')
            layer_input, fw_cache[i] = affine_bn_relu_forward(layer_input, self.params['W'+str(i+1)], 
                                                            self.params['b'+str(i+1)], self.params['gamma' + str(i+1)], 
                                                            self.params['beta' + str(i+1)], self.bn_params[i])

          else:
            # print('----in forward, no batchnorm, regular affine_relu_forward')
            layer_input, fw_cache[i] = affine_relu_forward(layer_input, self.params['W'+str(i+1)], self.params['b'+str(i+1)])
            # print('----after affine_relu_forward, layer_input.shape:',layer_input.shape)
          if self.use_dropout:
            # print('----in forward, use dropout, dropout_forward')
            layer_input, dp_cache[i] = dropout_forward(layer_input, self.dropout_param)
        # print('----in forward, last FC layer:')
        scores, fw_cache[self.num_layers] = affine_forward(layer_input,self.params['W'+str(self.num_layers)],self.params['b'+str(self.num_layers)])
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # print('----start backward----')
        reg = self.reg
        # print('----before calculate loss, scores:',scores)
        loss, dupgrade = softmax_loss(scores,y)
        dhout = dupgrade
        # print('----finish softmax loss, loss:',loss)
        # print('----dscore:',dhout)
        loss = loss + 0.5 * reg * (np.sum(self.params['W'+str(self.num_layers)] * self.params['W'+str(self.num_layers)]))
        # print('---- in backward, last FC layer plain affine_backward:')
        dx, dw, db = affine_backward(dupgrade, fw_cache[self.num_layers])

        grads['W'+str(self.num_layers)] = dw + reg * self.params['W'+str(self.num_layers)]
        grads['b' + str(self.num_layers)] = db
        dhout = dx
        for i in range(self.num_layers - 1):
          layer = self.num_layers - 1 - i - 1
          loss = loss + 0.5 * self.reg * np.sum(self.params['W'+str(layer+1)] * self.params['W' + str(layer+1)])
          # print('----at',layer,'layer----')
          # print('----dhout.shape:',dhout.shape)
          if self.use_dropout:
            # print('----use drop out')
            #print('fw_cache[layer]', dp_cache[layer])
            dhout = dropout_backward(dhout, dp_cache[layer])
            # print('dhout shape:',dhout.shape)
          
          if self.use_batchnorm:
            # print('----use batch normalization')
            dx, dw, db, dgamma, dbeta = affine_bn_relu_backward(dhout,fw_cache[layer])
            grads['gamma'+str(layer + 1)] = dgamma
            grads['beta'+str(layer + 1)]  = dbeta
          else:
            # print('----no bacth normalziation, affine_relu_backward')
            dx, dw, db = affine_relu_backward(dhout, fw_cache[layer])
            # print('----after affine_relu_backward, dx shape:', dx.shape)
          
          grads['W'+str(layer+1)] = dw + self.reg * self.params['W'+str(layer+1)]
          grads['b'+str(layer+1)] = db
          dhout = dx
          # print('----after one layer of backward, new upward gradient shape:',dupgrade.shape)

        # pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
