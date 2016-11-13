# coding:utf-8
'''
source code for train chatbot with DNC
'''
from DNC.DNC import DNC, optimizers, xp, Variable, cuda, np, _gpu_id
import chainer
from sklearn.externals import joblib


class ChatBot():
    def __init__(self):
        X = 5
        Y = 5
        N = 10*2
        W = 10*2
        R = 3*2
        self.mdl = DNC(X, Y, N, W, R)
        self.opt = optimizers.Adam()
        self.opt.setup(self.mdl)
        self.id2wordDict = {}
        self.word2idDict = {}
        self.loss = 0
        self.acc = 0

    def train(self, x_list, y_list):
        word_set = set()
        for each in x_list:
            word_set.update(each)
        for each in y_list:
            word_set.update(each)

        self.id2wordDict = dict(zip(range(len(word_set)), list(word_set)))
        self.word2idDict = dict(map(lambda (k, v): (v, k), self.id2wordDict.items()))
        model_dict = {'id2wordDict':self.id2wordDict,'word2idDict':self.word2idDict}
        for idx in range(50):

            lossfrac = xp.zeros((1, 2))
            for each_x, each_y in zip(x_list, y_list):
                input = map(lambda i: self.word2idDict[i], each_x)
                x = Variable(cuda.to_gpu(xp.array([input], np.float32), _gpu_id))
                output = map(lambda i: self.word2idDict[i], each_y)
                t = Variable(cuda.to_gpu(xp.array([output], np.float32), _gpu_id))
                y = self.mdl(x)
                if (isinstance(t, chainer.Variable)):
                    self.loss += (y - t) ** 2
                    is_equal = map(lambda i: int(i + 0.5), y.data[0]) == map(lambda i: int(i), t.data[0]), map(lambda i: int(i + 0.5), y.data[0]), map(
                        lambda i: int(i),
                        t.data[0])
                    try:
                        print "question:", " ".join(each_x)
                        print "answer:", " ".join(map(lambda i: self.id2wordDict[i], map(lambda i: int(i + 0.5), y.data[0])))
                    except Exception, e2:
                        print e2
                    # if idx==49:
                    #     print "BREAK!!"
                    #     break
                    if is_equal: self.acc += 1
                self.mdl.cleargrads()
                print '(', idx, ')', "loss:", self.loss.data[0].sum()

                self.loss.grad = xp.ones(self.loss.data.shape, dtype=np.float32)
                self.loss.backward()
                if idx>0:
                    self.opt.update()
                self.loss.unchain_backward()
                #             print '(', idx, ')', loss.data.sum()/loss.data.size/contentlen, acc/contentlen
                # lossfrac += xp.array([loss.data.sum() / loss.data.size / seqlen, 1.], np.float32)
                # if idx%5 == 0:
                #     model_dict['mdl'] = self.mdl
                #     joblib.dump(model_dict,"/home/dev/data/DNC_test.2.model")
                # loss = 0.0
                # acc = 0.0
                self.loss = 0
                self.acc = 0
                # break
                # input = map(lambda i: self.word2idDict[i], ["<start>", u"내일", u"비가", u"올까", "<eos>"])
                # x = Variable(cuda.to_gpu(xp.array([input], np.float32), _gpu_id))
                # y = self.mdl(x)
                # try:
                #     print "answer0:", " ".join(map(lambda i: self.id2wordDict[i], map(lambda i: int(i + 0.5), y.data[0])))
                # except Exception,e2:
                #     print e2
                #     continue


        input = map(lambda i: self.word2idDict[i], ["<start>", u"오늘", u"날씨가", u"어때", "<eos>"])
        x = Variable(cuda.to_gpu(xp.array([input], np.float32), _gpu_id))
        y = self.mdl.predict(x)
        print "answer1:", " ".join(map(lambda i: self.id2wordDict[i], map(lambda i: int(i + 0.5), y.data[0])))

                # model_dict['mdl'] = self.mdl
        # joblib.dump(model_dict, "/home/dev/data/DNC_test.2.model")

if __name__ == '__main__':
    input_list = [["<start>", u"오늘", u"날씨가", u"어때", "<eos>"], ["<start>", u"오늘", u"온도는", u"어때", "<eos>"], \
                  ["<start>", u"내일", u"비가", u"올까", "<eos>"]]
    output_list = [[u"화창하고", u"맑고", u"쾌적하고", u"좋습니다", "<eos>"], [u"오늘", u"온도는", u"무척", u"높습니다", "<eos>"], \
                   [u"내일은", u"비가", u"옵니다", "<eos>", ""]]
    chatbot = ChatBot()
    chatbot.train(input_list,output_list)
    joblib.dump(chatbot,"/home/dev/data/DNC_test.4.model")
    input = map(lambda i: chatbot.word2idDict[i], ["<start>", u"내일", u"비가", u"올까", "<eos>"])
    x = Variable(cuda.to_gpu(xp.array([input], np.float32), _gpu_id))
    y = chatbot.mdl.predict(x)
    print "answer2:", " ".join(map(lambda i: chatbot.id2wordDict[i], map(lambda i: int(i + 0.5), y.data[0])))


