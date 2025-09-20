from iptcinfo3 import IPTCInfo

# Baca IPTC
info = IPTCInfo('icon_-08.jpg')
print(info['object name'])  # Judul

# Tulis IPTC
info['object name'] = 'Foto Sunsetx' #judul
info['keywords'] = ['sack, arrow, down, bag, burlap, container, storage, symbol, sign, icon, outline, minimal, agriculture, farming, grain, harvest, product, package, cargo, delivery, shipping, direction, pointer, navigation, guide, element, design, graphic, isolated, clipart, simple, basic, shape, mark, pictogram, black, white, illustration, art, drawing, object, element, element, element, element'] #keywords
info['caption/abstract'] = 'Ini adalah deskripsi' #descriptions
info.save()
