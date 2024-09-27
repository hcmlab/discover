# import tensorflow as tf
# import io
# import numpy as np
# import io as inputoutput
# import base64
# import json
# import pickle
# import warnings
# import site as s
# from tensorflow.keras.models import load_model
# from PIL import Image
# from PIL import Image as pilimage
# from flask import Blueprint, Response, request
# from lime import lime_image
# from lime import lime_tabular
# from skimage.segmentation import mark_boundaries
#
# from nova_server.utils import explain_utils, img_utils
#
# # Initialization
# s.getusersitepackages()
# warnings.simplefilter("ignore")
# graph = tf.compat.v1.get_default_graph()
# explain = Blueprint("explain", __name__)
#
#
# @explain.route("/tfexplain", methods=["POST"])
# def explain_tfexplain():
#     global graph
#     data = {"success": "failed"}
#     #      # ensure an image was properly uploaded to our endpoint
#     if request.method == "POST":
#         if request.form.get("image"):
#
#             explainer = request.args.get("explainer")
#             # with graph.as_default():
#             model_path = request.form.get("model_path")
#             model = load_model(model_path)
#
#             # read the image in PIL format
#             image64 = request.form.get("image")
#             image = base64.b64decode(image64)
#             image = Image.open(io.BytesIO(image))
#             image = img_utils.prepare_image(image, target=(224, 224))
#             image = image * (1.0 / 255)
#             # img = tf.keras.preprocessing.image.img_to_array(image)
#             prediction = model.predict(image)
#             topClass = explain_utils.getTopXpredictions(prediction, 1)
#             print(topClass[0])
#             image = np.squeeze(image)
#
#             if explainer == "GRADCAM":
#                 im = ([image], None)
#                 from tf_explain.core.grad_cam import GradCAM
#
#                 exp = GradCAM()
#                 imgFinal = exp.explain(im, model, class_index=topClass[0][0])
#                 # exp.save(imgFinal, ".", "grad_cam.png")
#
#             elif explainer == "OCCLUSIONSENSITIVITY":
#                 im = ([image], None)
#                 from tf_explain.core.occlusion_sensitivity import OcclusionSensitivity
#
#                 exp = OcclusionSensitivity()
#                 imgFinal = exp.explain(
#                     im, model, class_index=topClass[0][0], patch_size=10
#                 )
#                 # exp.save(imgFinal, ".", "grad_cam.png")
#
#             elif explainer == "GRADIENTSINPUTS":
#                 im = (np.array([image]), None)
#                 from tf_explain.core.gradients_inputs import GradientsInputs
#
#                 exp = GradientsInputs()
#                 imgFinal = exp.explain(im, model, class_index=topClass[0][0])
#                 # exp.save(imgFinal, ".", "gradients_inputs.png")
#
#             elif explainer == "VANILLAGRADIENTS":
#                 im = (np.array([image]), None)
#                 from tf_explain.core.vanilla_gradients import VanillaGradients
#
#                 exp = VanillaGradients()
#                 imgFinal = exp.explain(im, model, class_index=topClass[0][0])
#                 # exp.save(imgFinal, ".", "gradients_inputs.png")
#
#             elif explainer == "SMOOTHGRAD":
#                 im = (np.array([image]), None)
#                 from tf_explain.core.smoothgrad import SmoothGrad
#
#                 exp = SmoothGrad()
#                 imgFinal = exp.explain(im, model, class_index=topClass[0][0])
#                 # exp.save(imgFinal, ".", "gradients_inputs.png")
#
#             elif explainer == "INTEGRATEDGRADIENTS":
#                 im = (np.array([image]), None)
#                 from tf_explain.core.integrated_gradients import IntegratedGradients
#
#                 exp = IntegratedGradients()
#                 imgFinal = exp.explain(im, model, class_index=topClass[0][0])
#                 # exp.save(imgFinal, ".", "gradients_inputs.png")
#
#             elif explainer == "ACTIVATIONVISUALIZATION":
#                 # need some solution to find out and submit layers name
#                 im = (np.array([image]), None)
#                 from tf_explain.core.activations import ExtractActivations
#
#                 exp = ExtractActivations()
#                 imgFinal = exp.explain(im, model, layers_name=["activation_1"])
#                 # exp.save(imgFinal, ".", "gradients_inputs.png")
#
#             img = pilimage.fromarray(imgFinal)
#             imgByteArr = inputoutput.BytesIO()
#             img.save(imgByteArr, format="JPEG")
#             imgByteArr = imgByteArr.getvalue()
#
#             img64 = base64.b64encode(imgByteArr)
#             img64_string = img64.decode("utf-8")
#
#             data["explanation"] = img64_string
#             data["prediction"] = str(topClass[0][0])
#             data["prediction_score"] = str(topClass[0][1])
#             data["success"] = "success"
#
#     return Response(json.dumps(data), mimetype="text/plain")
#
#
# @explain.route("/innvestigate", methods=["POST"])
# def explain_innvestigate():
#     global graph
#     data = {"success": "failed"}
#     # ensure an image was properly uploaded to our endpoint
#     if request.method == "POST":
#         if request.form.get("image"):
#
#             postprocess = request.args.get("postprocess")
#             explainer = request.args.get("explainer")
#             lrpalpha = float(request.args.get("lrpalpha"))
#             lrpbeta = float(request.args.get("lrpbeta"))
#
#             with graph.as_default():
#                 model_path = request.form.get("model_path")
#                 model = load_model(model_path)
#
#                 # read the image in PIL format
#                 image64 = request.form.get("image")
#                 image = base64.b64decode(image64)
#                 image = Image.open(io.BytesIO(image))
#
#                 # preprocess the image and prepare it for classification
#                 image = img_utils.prepare_image(image, target=(224, 224))
#                 image = image * (1.0 / 255)
#
#                 # print(model.summary())
#                 model_wo_sm = iutils.keras.graph.model_wo_softmax(model)
#
#                 prediction = model.predict(image)
#                 topClass = explain_utils.getTopXpredictions(prediction, 1)
#
#                 model_wo_sm = iutils.keras.graph.model_wo_softmax(model)
#
#                 analyzer = []
#
#                 if explainer == "GUIDEDBACKPROP":
#                     analyzer = innvestigate.analyzer.GuidedBackprop(model_wo_sm)
#                 elif explainer == "GRADIENT":
#                     analyzer = innvestigate.analyzer.Gradient(model_wo_sm)
#                 elif explainer == "DECONVNET":
#                     analyzer = innvestigate.analyzer.Deconvnet(model_wo_sm)
#                 elif explainer == "LRPEPSILON":
#                     analyzer = innvestigate.analyzer.LRPEpsilon(model_wo_sm)
#                 elif explainer == "LRPZ":
#                     analyzer = innvestigate.analyzer.LRPZ(model_wo_sm)
#                 elif explainer == "LRPALPHABETA":
#                     analyzer = innvestigate.analyzer.LRPAlphaBeta(
#                         model_wo_sm, alpha=lrpalpha, beta=lrpbeta
#                     )
#                 elif explainer == "DEEPTAYLOR":
#                     analyzer = innvestigate.analyzer.DeepTaylor(model_wo_sm)
#
#                 # Applying the analyzer
#                 analysis = analyzer.analyze(image)
#
#                 imgFinal = []
#
#                 if postprocess == "GRAYMAP":
#                     imgFinal = explain_utils.graymap(analysis)[0]
#                 elif postprocess == "HEATMAP":
#                     imgFinal = explain_utils.heatmap(analysis)[0]
#                 elif postprocess == "BK_PROJ":
#                     imgFinal = explain_utils.bk_proj(analysis)[0]
#                 elif postprocess == "GNUPLOT2":
#                     imgFinal = explain_utils.heatmapgnuplot2(analysis)[0]
#                 elif postprocess == "CMRMAP":
#                     imgFinal = explain_utils.heatmapCMRmap(analysis)[0]
#                 elif postprocess == "NIPY_SPECTRAL":
#                     imgFinal = explain_utils.heatmapnipy_spectral(analysis)[0]
#                 elif postprocess == "RAINBOW":
#                     imgFinal = explain_utils.heatmap_rainbow(analysis)[0]
#                 elif postprocess == "INFERNO":
#                     imgFinal = explain_utils.heatmap_inferno(analysis)[0]
#                 elif postprocess == "GIST_HEAT":
#                     imgFinal = explain_utils.heatmap_gist_heat(analysis)[0]
#                 elif postprocess == "VIRIDIS":
#                     imgFinal = explain_utils.heatmap_viridis(analysis)[0]
#
#                 imgFinal = np.uint8(imgFinal * 255)
#
#                 img = pilimage.fromarray(imgFinal)
#                 imgByteArr = inputoutput.BytesIO()
#                 img.save(imgByteArr, format="JPEG")
#                 imgByteArr = imgByteArr.getvalue()
#
#                 img64 = base64.b64encode(imgByteArr)
#                 img64_string = img64.decode("utf-8")
#                 data["explanation"] = img64_string
#                 data["prediction"] = str(topClass[0][0])
#                 data["prediction_score"] = str(topClass[0][1])
#                 data["success"] = "success"
#
#     return Response(json.dumps(data), mimetype="text/plain")
#
#
# @explain.route("/lime", methods=["POST"])
# def explain_lime():
#     global graph
#     data = {"success": "failed"}
#
#     if request.method == "POST":
#         if request.form.get("image"):
#
#             top_labels = int(request.args.get("toplabels"))
#             hide_color = str(request.args.get("hidecolor"))
#             num_samples = int(request.args.get("numsamples"))
#             positive_only = str(request.args.get("positiveonly"))
#             num_features = int(request.args.get("numfeatures"))
#             hide_rest = str(request.args.get("hiderest"))
#
#             # read the image in PIL format
#             image64 = request.form.get("image")
#             image = base64.b64decode(image64)
#             image = Image.open(io.BytesIO(image))
#
#             with graph.as_default():
#
#                 model_path = request.form.get("model_path")
#                 model = load_model(model_path)
#
#                 img = img_utils.prepare_image(image, (224, 224))
#                 img = img * (1.0 / 255)
#                 prediction = model.predict(img)
#                 explainer = lime_image.LimeImageExplainer()
#                 img = np.squeeze(img).astype("double")
#                 explanation = explainer.explain_instance(
#                     img,
#                     model.predict,
#                     top_labels=top_labels,
#                     hide_color=hide_color == "True",
#                     num_samples=num_samples,
#                 )
#
#                 top_classes = explain_utils.getTopXpredictions(prediction, top_labels)
#
#                 explanations = []
#
#                 for cl in top_classes:
#                     temp, mask = explanation.get_image_and_mask(
#                         cl[0],
#                         positive_only=positive_only == "True",
#                         num_features=num_features,
#                         hide_rest=hide_rest == "True",
#                     )
#                     img_explained = mark_boundaries(temp, mask)
#                     img = Image.fromarray(np.uint8(img_explained * 255))
#                     img_byteArr = io.BytesIO()
#                     img.save(img_byteArr, format="JPEG")
#                     img_byteArr = img_byteArr.getvalue()
#                     img64 = base64.b64encode(img_byteArr)
#                     img64_string = img64.decode("utf-8")
#
#                     explanations.append((str(cl[0]), str(cl[1]), img64_string))
#
#                 data["explanations"] = explanations
#                 data["success"] = "success"
#
#     return Response(json.dumps(data), mimetype="text/plain")
#
#
# @explain.route("/tabular", methods=["POST"])
# def explain_tabular():
#     data = {"success": "failed"}
#
#     # TODO send sample to be explained
#
#     if request.method == "POST":
#
#         if request.form:
#
#             # data_dict = ast.literal_eval(json.loads(flask.request.data))
#
#             print("try open model")
#             with open(request.form.get("model_path"), "rb") as f:
#                 model = pickle.load(f)
#
#             train_data = json.loads(request.form.get("data"))
#             dim = json.loads(request.form.get("dim"))
#             train_data = np.asarray(train_data)
#             train_data = train_data.reshape(((int)(train_data.size / dim), dim))
#             sample = json.loads(request.form.get("sample"))
#
#             num_features = int(request.args.get("numfeatures"))
#
#             explainer = lime_tabular.LimeTabularExplainer(
#                 train_data, mode="classification", discretize_continuous=True
#             )
#             exp = explainer.explain_instance(
#                 np.asarray(sample),
#                 model.predict_proba,
#                 num_features=num_features,
#                 top_labels=1,
#             )
#
#             explanation_dictionary = {}
#
#             for entry in exp.as_list():
#                 explanation_dictionary.update({entry[0]: entry[1]})
#
#             data["explanation"] = explanation_dictionary
#             data["success"] = "success"
#
#     return Response(json.dumps(data), mimetype="text/plain")
