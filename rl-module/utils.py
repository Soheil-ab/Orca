'''
MIT License
Copyright (c) Chen-Yu Yen - Soheil Abbasloo 2020
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import numpy as np
import logging
import os
import json
import random


def configure_logging(path_to_log_directory):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not os.path.exists(path_to_log_directory):
        os.makedirs(path_to_log_directory)
    handler = logging.FileHandler(filename=os.path.join(path_to_log_directory, "result.log"))

    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

logger = configure_logging("./rl_logging")



class G_Noise(object):
    def __init__(self, mu , sigma, explore=40000,theta=0.1,mu2=0.0,mode="exp",eps=1.0,step=0.3):
        self.epsilon = eps
        self.mu = mu
        self.explore = explore
        self.sigma = sigma
        self.mu2 = mu2
        self.theta = theta
        self.noise = 0
        self.cnt = 0
        self.step = step
        self.mode = mode

    def show(self):
        return self.noise

    def __call__(self,point):
        if self.explore!=None:
            if self.mode=="exp":
                if self.epsilon <= 0:
                    self.noise=np.zeros_like(self.mu)
                else:
                    self.epsilon -= 1/self.explore
                    noise = self.epsilon * (self.sigma * np.random.randn(1))
                    self.noise = noise
            else:
                self.cnt += 1
                if self.cnt >=self.explore:
                    self.sigma -= self.step*self.sigma
                    self.cnt = 0
                if self.sigma <= 0.1:
                    self.segma = 0.1
                noise = self.sigma*np.random.randn(1)
                self.noise = noise
        else:
            noise = (self.sigma * np.random.randn(1))
            self.noise = noise

        return self.noise

    def reset(self):
        pass


class OU_Noise:
    def __init__(self, mu, sigma, theta=.15, dt=0.01, x0=None,exp=None):
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.x0 = x0
        self.eps = 1.0
        self.exp = exp
        self.reset()

    def show(self):
        return self.x_prev

    def __call__(self,point):
        if self.exp!=None:
            self.dt -= 1/self.exp
            if self.dt<=0.01:
                self.dt=0.01
            self.sigma -= 1/self.exp
            if self.sigma<=0.3:
                self.sigma=0.3

        x = self.x_prev + self.theta * (self.mu - self.x_prev) * self.dt + self.sigma * np.sqrt(self.dt) * np.random.normal(size=self.mu.shape)
        self.x_prev = x
        return x

    def reset(self):
        self.x_prev = self.x0 if self.x0 is not None else np.zeros_like(self.mu)



class ReplayBuffer:

    def __init__(self, size, s_dim, a_dim, batch_size):
        self.size = size
        self.s0_buf = np.zeros((size, s_dim), dtype=np.float32)
        self.a_buf = np.zeros((size, a_dim), dtype=np.float32)
        self.reward_buf = np.zeros((size,1), dtype=np.float32)
        self.s1_buf = np.zeros((size, s_dim), dtype=np.float32)
        self.terminal_buf = np.zeros((size,1), dtype=np.float32)
        self.ptr = 0
        self.full = False
        self.batch_size = batch_size

        self.length_buf = 0



    def peek_buffer(self):
        return [self.s0_buf, self.a_buf, self.reward_buf, self.s1_buf, self.terminal_buf]

    def store(self, s0, a, r, s1, terminal):
        self.s0_buf[self.ptr] = s0
        self.a_buf[self.ptr] = a
        self.reward_buf[self.ptr] = r
        self.s1_buf[self.ptr] = s1
        self.terminal_buf[self.ptr] = terminal
        self.ptr += 1

        # Buffer Full
        if self.ptr == self.size:
            self.ptr = 0
            self.full = True
            self.length_buf = self.size
        if self.full == False:
            self.length_buf = self.ptr


    def store_many(self, s0, a, r, s1, terminal, length):
        if self.ptr + length >= self.size:
            firstpart = self.size-self.ptr
            secondpart = length - firstpart
            self.s0_buf[self.ptr:] = s0[:firstpart]
            self.s0_buf[:secondpart] = s0[firstpart:]

            self.a_buf[self.ptr:] = a[:firstpart]
            self.a_buf[:secondpart] = a[firstpart:]

            self.reward_buf[self.ptr:] = r[:firstpart]
            self.reward_buf[:secondpart] = r[firstpart:]

            self.s1_buf[self.ptr:] = s1[:firstpart]
            self.s1_buf[:secondpart] = s1[firstpart:]

            self.terminal_buf[self.ptr:] = terminal[:firstpart]
            self.terminal_buf[:secondpart] = terminal[firstpart:]

            self.ptr= secondpart
            self.full = True

        else:

            self.s0_buf[self.ptr: self.ptr+length] = s0
            self.a_buf[self.ptr: self.ptr+length] = a
            self.reward_buf[self.ptr: self.ptr+length] = r
            self.s1_buf[self.ptr: self.ptr+length] = s1
            self.terminal_buf[self.ptr: self.ptr+length] = terminal

            self.ptr += length

        if self.full:
            self.length_buf = self.size
        else:
            self.length_buf = self.ptr


    def sample(self):
        import random
        if self.batch_size < self.length_buf :
            start_index = int(self.length_buf*random.random())
            if start_index + self.batch_size >= self.length_buf:
                arr1 = list(range(start_index, self.length_buf))
                arr2 = list(range(0, self.batch_size- len(arr1)))
                index = arr1 + arr2
            else:
                index = list(range(start_index, start_index+self.batch_size))

        else:
            index = list(range(0, self.length_buf))


        s0 = self.s0_buf[index]
        a = self.a_buf[index]
        r = self.reward_buf[index]
        s1 = self.s1_buf[index]
        terminal = self.terminal_buf[index]

        return [s0, a, r, s1, terminal]


    def _encode_sample(self, idxes):

        s0 = self.s0_buf[idxes]
        a = self.a_buf[idxes]
        r = self.reward_buf[idxes]
        s1 = self.s1_buf[idxes]
        terminal = self.terminal_buf[idxes]

        return [s0, a, r, s1, terminal]


class Prioritized_ReplayBuffer(ReplayBuffer):

    def __init__(self, size, s_dim, a_dim, batch_size, alpha=1):
        pass

    def store(self, *args, **kwargs):
        pass

    def _sample_proportional(self, batch_size):
        pass

    def sample(self, beta=0.5):
        pass

    def update_priorities(self, idxes, priorities):
        pass


class Params():

    def __init__(self, json_path):
        self.update(json_path)

    def save(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        return self.__dict__
