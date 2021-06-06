import glob

from tqdm import tqdm

from apparel_styles.ml_src.preprocessing import get_attribute_dims
from apparel_styles.ml_src.classifiers import get_pretrained_model, create_attributes_model, AttributeFCN, \
    predict_attributes

# Labels File
LABEL_DIR = "apparel_styles/ml_src/data/ClothingAttributeDataset/labels/"
labels_file = "apparel_styles/ml_src/data/labels.csv"
label_values_file = "apparel_styles/ml_src/data/label_values.json"

if __name__ == "__main__":
    target_dims = get_attribute_dims(label_values_file)
    pretrained_conv_model, _, _ = get_pretrained_model("vgg16", pop_last_pool_layer=True, use_gpu=False)
    attribute_models = create_attributes_model(AttributeFCN, 512, pretrained_conv_model,
                                               target_dims,
                                               weights_root="apparel_styles/ml_src/weights/vgg16-fcn-266-2/",
                                               labels_file=labels_file,
                                               use_gpu=None,
                                               is_train=False,
                                               train_images_folder=None)

    images = glob.glob("query_1_transformed_images/*")
    res = []
    for img in tqdm(images):
        res.append(predict_attributes(img, pretrained_conv_model, attribute_models, attribute_idx_map=None,
                                 flatten_pretrained_out=False, use_gpu=None))
    print(res)

