import os
import torch
import torch.utils.data
import PIL
from PIL import Image
import re
from datasets.data_augment import PairCompose, PairRandomCrop, PairToTensor

class LLdataset:
    def __init__(self, config):
        self.config = config
        self.create_file_list_if_not_exists()

    def create_file_list_if_not_exists(self):
        """
        Create text files listing all images in the train and val directories if they do not exist.
        """
        def create_file_list(data_dir, dataset_name, phase):
            dataset_dir = os.path.join(data_dir, dataset_name, phase)
            file_list_path = os.path.join(data_dir, dataset_name, f'{dataset_name}_{phase}.txt')

            if not os.path.exists(file_list_path):
                with open(file_list_path, 'w') as file_list:
                    for root, dirs, files in os.walk(dataset_dir):
                        for file in files:
                            if file.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                                file_list.write(os.path.join(root, file) + '\n')

                print(f"{phase} list created at: {file_list_path}")

        data_dir = self.config.data.data_dir
        train_dataset_name = self.config.data.train_dataset
        val_dataset_name = self.config.data.val_dataset

    #     create_file_list(data_dir, train_dataset_name, 'train')
    #     create_file_list(data_dir, val_dataset_name, 'val')

    # def get_loaders(self):
    #     train_dataset = AllWeatherDataset(os.path.join(self.config.data.data_dir, self.config.data.train_dataset, 'train'),
    #                                       patch_size=self.config.data.patch_size,
    #                                       filelist='{}_train.txt'.format(self.config.data.train_dataset))
    #     val_dataset = AllWeatherDataset(os.path.join(self.config.data.data_dir, self.config.data.val_dataset, 'val'),
    #                                     patch_size=self.config.data.patch_size,
    #                                     filelist='{}_val.txt'.format(self.config.data.val_dataset), train=False)

    #     train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.config.training.batch_size,
    #                                                shuffle=True, num_workers=self.config.data.num_workers,
    #                                                pin_memory=True)
    #     val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=1, shuffle=False,
    #                                              num_workers=self.config.data.num_workers,
    #                                              pin_memory=True)

    #     return train_loader, val_loader
        create_file_list(data_dir, train_dataset_name, 'train')
        create_file_list(data_dir, val_dataset_name, 'test')

    def get_loaders(self):
        train_dataset = AllWeatherDataset(os.path.join(self.config.data.data_dir, self.config.data.train_dataset, 'train'),
                                          patch_size=self.config.data.patch_size,
                                          filelist='{}_train.txt'.format(self.config.data.train_dataset))
        test_dataset = AllWeatherDataset(os.path.join(self.config.data.data_dir, self.config.data.val_dataset, 'test'),
                                        patch_size=self.config.data.patch_size,
                                        filelist='{}_test.txt'.format(self.config.data.val_dataset), train=False)


        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.config.training.batch_size,
                                                   shuffle=True, num_workers=self.config.data.num_workers,
                                                   pin_memory=True)
        val_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False,
                                                 num_workers=self.config.data.num_workers,
                                                 pin_memory=True)

        return train_loader, val_loader

class AllWeatherDataset(torch.utils.data.Dataset):
    def __init__(self, dir, patch_size, filelist=None, train=True):
        super().__init__()

        self.dir = dir
        self.train = train
        self.file_list = filelist
        self.train_list = os.path.join(dir, self.file_list)
        with open(self.train_list) as f:
            contents = f.readlines()
            input_names = [i.strip() for i in contents]
            gt_names = [i.strip().replace('low', 'high') for i in input_names]

        self.input_names = input_names
        self.gt_names = gt_names
        self.patch_size = patch_size
        if self.train:
            self.transforms = PairCompose([
                PairRandomCrop(self.patch_size),
                PairToTensor()
            ])
        else:
            self.transforms = PairCompose([
                PairToTensor()
            ])

    def get_images(self, index):
        input_name = self.input_names[index].replace('\n', '')
        gt_name = self.gt_names[index].replace('\n', '')
        img_id = re.split('/', input_name)[-1][:-4]
        input_img = Image.open(os.path.join(self.dir, input_name)) if self.dir else PIL.Image.open(input_name)
        gt_img = Image.open(os.path.join(self.dir, gt_name)) if self.dir else PIL.Image.open(gt_name)

        input_img, gt_img = self.transforms(input_img, gt_img)

        return torch.cat([input_img, gt_img], dim=0), img_id

    def __getitem__(self, index):
        res = self.get_images(index)
        return res

    def __len__(self):
        return len(self.input_names)
