from Recommender.model import MFModel
import os
import sys
import numpy as np
import torch

ROOT_PATH = os.path.abspath(os.path.dirname(__file__)).split('Recommender')[0] + 'Recommender'
sys.path.append(ROOT_PATH)


class MovieRecommender:
    def __init__(self, config):
        self.config = config
        self.device = torch.device(config['device'])
        self.set_seed()
        self.model = None

    def set_seed(self):
        if self.config['fix_seed']:
            import os
            seed = self.config['seed']
            os.environ['PYTHONHASHSEED'] = str(seed)

            import random
            random.seed(seed)
            np.random.seed(seed)

            import torch
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True

    def model_init(self):
        user_num, item_num = 943, 1682
        if self.config['model'].lower() == 'mf':
            model = MFModel(user_num, item_num, self.config['emb_dim'])
            model.load_state_dict(torch.load(self.config['weight_path']))

            self.model = model.to(self.device)
        else:
            raise ValueError('Not supported model types')

    def topk(self, user_id, k):
        self.model_init()

        if not isinstance(user_id, list):
            user_id = [user_id]
        user_id = torch.LongTensor(user_id).to(self.device)

        query = self.model.construct_query(user_id)
        score, topk_items = torch.topk(self.model.scorer(query, self.model.item_encoder.weight[1:]), k)

        if len(user_id) == 1:
            return topk_items.cpu().numpy()[0]
        else:
            return topk_items.cpu().numpy()


if __name__ == '__main__':
    config = {
        'emb_dim': 32,
        'weight_path': '../ml-100k_sslpop.pt',
        'device': 'cuda',
        'model': 'mf',
        'seed': 10,
        'fix_seed': True,
    }
    recomender = MovieRecommender(config)
    user_ids = [1,2,3]
    items = recomender.topk(user_ids, 10)

    print(items)