'''
MIT License
Copyright (c) Soheil Abbasloo - Chen-Yu Yen 2020

Permission is hereby granted, free of charge, to any person obtaining a copy
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
import gym
import math
import collections
from utils import logger
import os
import sysv_ipc
import signal
import sys
from time import sleep

class Env_Wrapper(object):
    def __init__(self, name):

        self.env = gym.make(name)
        self.env.reset()

    def get_dims_info(self):

        return self.env.observation_space.shape[0], self.env.action_space.shape[0]

    def get_action_info(self):
        action_scale = self.env.action_space.high
        action_range = (self.env.action_space.low, self.env.action_space.high)
        return  action_scale, action_range

    def reset(self):
        return self.env.reset()

    def step(self, action,eval_=False):
        s1, r, done, _ = self.env.step(action)

        if done:
            s1 = self.env.reset()

        return s1, r, done, _



class GYM_Env_Wrapper(Env_Wrapper):
    def __init__(self,name, params, for_init_only=True, shrmemory_id=None, shrmem_r=None, shrmem_w=None):
        super().__init__(name)
        logger.info("USE_GYM_Env_Wrapper")
        if not for_init_only:
            self.shrmemory_id = shrmemory_id
            self.shrmem_r = shrmem_r
            self.shrmem_w = shrmem_w
            self.prev_rid = 99

    def test(self):
        print("Hello")

    def get_state(self):

        prev_rid = 0
        s1 = None
        delay_ = 0
        rew0 = 10
        error_code = True
        return prev_rid, s1, delay_, rew0, error_code

    def write_action(self, action):
        pass

    def map_action(self, action):
        out = math.pow(4, action)
        out *= 100
        out = int(out)
        return out

    def step(self, action, eval_=False):

        s1, r, done, _ = self.env.step(action)

        if done:
            s1 = self.env.reset()

        return s1, r, done, True


class TCP_Env_Wrapper(object):
    def __init__(self,name, params, config=None, for_init_only=True, shrmem_r=None, shrmem_w=None,use_normalizer=True):

        self.params = params
        if not for_init_only:
            self.params = params
            self.shrmem_r = shrmem_r
            self.shrmem_w = shrmem_w
            self.prev_rid = 99999
            self.wid = 23
            self.local_counter=0
            self.pre_samples = 0.0
            self.new_samples = 0.0
            self.avg_delay = 0.0
            self.avg_thr = 0.0
            self.thr_ = 0.0
            self.del_ = 0.0
            self.max_bw = 0.0
            self.max_cwnd = 0.0
            self.max_smp = 0.0
            self.min_del = 9999999.0

            self.use_normalizer=use_normalizer
            if self.use_normalizer==True:
                self.normalizer=Normalizer(params, config)
            else:
                self.normalizer=None
            self.del_moving_win = Moving_Win(params.dict['MVWIN'])
            self.thr_moving_win = Moving_Win(params.dict['MVWIN'])
            self.config = config
            signal.signal(signal.SIGINT, self.handler_term)
            signal.signal(signal.SIGTERM, self.handler_term)
            if self.config.load is not None and self.use_normalizer==True:
                _ = self.normalizer.load_stats()

    def handler_term(self, signum, frame):
        print("python program terminated usking Kill -15")
        if not self.config.eval and self.use_normalizer==True:
            print("save stats by kill -15")
            self.normalizer.save_stats()
        sys.exit(0)

    def get_dims_info(self):
        return self.params.dict['state_dim'], self.params.dict['action_dim']

    def get_action_info(self):
        action_scale = np.array([1.])
        action_range = (-action_scale,action_scale)
        print('action_scale & action_range')
        return  action_scale, action_range

    def reset(self):
        # start signal
        self.shrmem_w.write(str(99999) + " " + str(99999) + "\0")
        state, delay_, rew0, error_code  = self.get_state()
        return state

    def test(self):
        print("Hello")



    def get_state(self, evaluation=False):
        succeed = False
        error_cnt=0
        while(1):
        # Read value from shared memory
            try:
                memory_value = self.shrmem_r.read()

            except sysv_ipc.ExistentialError:
                print("No shared memory Now, python ends gracefully :)")
                logger.info("No shared memory Now, python ends gracefully :)")
                sys.exit(0)

            memory_value = memory_value.decode('unicode_escape')

            i = memory_value.find('\0')

            if i != -1:

                memory_value = memory_value[:i]
                readstate = np.fromstring(memory_value, dtype=float, sep=' ')
                try:
                    rid = readstate[0]
                except :
                    rid = self.prev_rid
                    sleep(0.01)
                    continue
                try:
                    s0 = readstate[1:]
                except :
                    print("s0 waring")
                    sleep(0.01)
                    continue


                if rid != self.prev_rid:
                    succeed = True
                    break
                else:
                    wwwwww=""

            error_cnt=error_cnt+1
            if error_cnt > 24000:
                error_cnt=0
                print("After 3 min, We didn't get any state from the server. Actor "+str(self.config.task)+" is going down down down ...\n")
                sys.exit(0)

            sleep(0.01)

        error_cnt=0
        if succeed == False:
            raise ValueError('read Nothing new from shrmem for a long time')
        reward=0
        state=np.zeros(1)
        w=s0
        if len(s0) == (self.params.dict['input_dim']):
            d=s0[0]
            thr=s0[1]
            samples=s0[2]
            delta_t=s0[3]
            target_=s0[4]
            cwnd=s0[5]
            pacing_rate=s0[6]
            loss_rate=s0[7]
            srtt_ms=s0[8]
            snd_ssthresh=s0[9]
            packets_out=s0[10]
            retrans_out=s0[11]
            max_packets_out=s0[12]
            mss=s0[13]
            min_rtt=s0[14]

            self.local_counter+=1

            if self.use_normalizer==True:
                if evaluation!=True:
                    self.normalizer.observe(s0)
                s0 = self.normalizer.normalize(s0)
                min_ = self.normalizer.stats()
            else:
                min_ = s0-s0

            d_n=s0[0]-min_[0]
            thr_n=s0[1]
            thr_n_min=s0[1]-min_[1]
            samples_n=s0[2]
            samples_n_min=s0[2]-min_[2]
            delta_t_n=s0[3]
            delta_t_n_min=s0[3]-min_[3]

            cwnd_n_min=s0[5]-min_[5]
            pacing_rate_n_min=s0[6]-min_[6]
            loss_rate_n_min=s0[7]-min_[7]
            srtt_ms_min=s0[8]-min_[8]
            snd_ssthresh_min=s0[9]-min_[9]
            packets_out_min=s0[10]-min_[10]
            retrans_out_min=s0[11]-min_[11]
            max_packets_out_min=s0[12]-min_[12]
            mss_min=mss-min_[13]
            min_rtt_min=min_rtt-min_[14]

            if self.use_normalizer==False:
                thr_n=thr_n
                thr_n_min=thr_n_min
                samples_n_min=samples_n_min
                cwnd_n_min=cwnd_n_min
                loss_rate_n_min=loss_rate_n_min
                d_n=d_n
            if self.max_bw<thr_n_min:
                self.max_bw=thr_n_min
            if self.max_cwnd<cwnd_n_min:
                self.max_cwnd=cwnd_n_min
            if self.max_smp<samples_n_min:
                self.max_smp=samples_n_min
            if self.min_del>d_n:
                self.min_del=d_n

            ################# Transfer all of the vars. to Rate/Max(Rate) space
            #cwnd_bytes= cwnd_n_min*mss_min
            #cwnd_n_min=(cwnd_bytes*1000)/srtt_ms_min
            #snd_ssthresh_min=(snd_ssthresh_min*mss_min*1000)/srtt_ms_min
            #packets_out_min=(packets_out_min*mss_min*1000)/srtt_ms_min
            #retrans_out_min=(retrans_out_min*mss_min*1000)/srtt_ms_min
            #max_packets_out_min=(max_packets_out_min*mss_min*1000)/srtt_ms_min
            #inflight_bytes=(packets_out-samples)*mss_min*1000

            if min_rtt_min*(self.params.dict['delay_margin_coef'])<srtt_ms_min:
                delay_metric=(min_rtt_min*(self.params.dict['delay_margin_coef']))/srtt_ms_min
            else:
                delay_metric=1

            reward  = (thr_n_min-5*loss_rate_n_min)/self.max_bw*delay_metric

            if self.max_bw!=0:
                state[0]=thr_n_min/self.max_bw
                tmp=pacing_rate_n_min/self.max_bw
                if tmp>10:
                    tmp=10
                state=np.append(state,[tmp])
                state=np.append(state,[5*loss_rate_n_min/self.max_bw])
            else:
                state[0]=0
                state=np.append(state,[0])
                state=np.append(state,[0])
            state=np.append(state,[samples/cwnd])
            state=np.append(state,[delta_t_n])
            state=np.append(state,[min_rtt_min/srtt_ms_min])
            state=np.append(state,[delay_metric])

            self.prev_rid = rid
            return state, d, reward, True
        else:
            return state, 0.0, reward, False

    def map_action(self, action):
        out = math.pow(4, action)
        out *= 100
        out = int(out)
        return out

    def map_action_reverse(self,a):
        out =  math.log(a/100,4)
        return out


    def write_action(self, action):

        modified_action = self.map_action(action)

        msg = str(self.wid)+" "+str(modified_action)+"\0"
        self.shrmem_w.write(msg)
        self.wid = (self.wid + 1) % 1000
        pass

    def step(self, action, eval_=False):
        s1, delay_, rew0, error_code  = self.get_state(evaluation=eval_)

        return s1, rew0, False, error_code


class Moving_Win():
    def __init__(self,win_size):
        self.queue_main = collections.deque(maxlen=win_size)
        self.queue_aux = collections.deque(maxlen=win_size)
        self.length = 0
        self.avg = 0.0
        self.size = win_size
        self.total_samples=0

    def push(self,sample_value,sample_num):
        if self.length<self.size:
            self.queue_main.append(sample_value)
            self.queue_aux.append(sample_num)
            self.length=self.length+1
            self.avg=(self.avg*self.total_samples+sample_value*sample_num)
            self.total_samples+=sample_num
            if self.total_samples>0:
                self.avg=self.avg/self.total_samples
            else:
                self.avg=0.0
        else:
            pop_value=self.queue_main.popleft()
            pop_num=self.queue_aux.popleft()
            self.queue_main.append(sample_value)
            self.queue_aux.append(sample_num)
            self.avg=(self.avg*self.total_samples+sample_value*sample_num-pop_value*pop_num)
            self.total_samples=self.total_samples+(sample_num-pop_num)
            if self.total_samples>0:
                self.avg=self.avg/self.total_samples
            else:
                self.avg=0.0

    def get_avg(self):
        return self.avg

    def get_length(self):
        return self.length

class Normalizer():
    def __init__(self, params, config):
        self.params = params
        self.config = config
        self.n = 1e-5
        num_inputs = self.params.dict['input_dim']
        self.mean = np.zeros(num_inputs)
        self.mean_diff = np.zeros(num_inputs)
        self.var = np.zeros(num_inputs)
        self.dim = num_inputs
        self.min = np.zeros(num_inputs)


    def observe(self, x):
        self.n += 1
        last_mean = np.copy(self.mean)
        self.mean += (x-self.mean)/self.n
        self.mean_diff += (x-last_mean)*(x-self.mean)
        self.var = self.mean_diff/self.n

    def normalize(self, inputs):
        obs_std = np.sqrt(self.var)
        a=np.zeros(self.dim)
        if self.n > 2:
            a=(inputs - self.mean)/obs_std
            for i in range(0,self.dim):
                if a[i] < self.min[i]:
                    self.min[i] = a[i]
            return a
        else:
            return np.zeros(self.dim)

    def normalize_delay(self,delay):
        obs_std = math.sqrt(self.var[0])
        if self.n > 2:
            return (delay - self.mean[0])/obs_std
        else:
            return 0

    def stats(self):
        return self.min

    def save_stats(self):
        dic={}
        dic['n']=self.n
        dic['mean'] = self.mean.tolist()
        dic['mean_diff'] = self.mean_diff.tolist()
        dic['var'] = self.var.tolist()
        dic['min'] = self.min.tolist()
        import json
        with open(os.path.join(self.params.dict['train_dir'], 'stats.json'), 'w') as fp:
                json.dump(dic, fp)

        print("--------save stats at{}--------".format(self.params.dict['train_dir']))
        logger.info("--------save stats at{}--------".format(self.params.dict['train_dir']))



    def load_stats(self, file='stats.json'):
        import json
        if os.path.isfile(os.path.join(self.params.dict['train_dir'], file)):
            print("Stats exist!, load", self.config.task)
            with open(os.path.join(self.params.dict['train_dir'], file), 'r') as fp:
                history_stats = json.load(fp)
                print(history_stats)
            self.n = history_stats['n']
            self.mean = np.asarray(history_stats['mean'])
            self.mean_diff = np.asarray(history_stats['mean_diff'])
            self.var = np.asarray(history_stats['var'])
            self.min = np.asarray(history_stats['min'])
            return True
        else:
            print("stats file is missing when loading")
            return False

