def get_keys(data_type):
    tag_map = get_tag_map(data_type)
    try:
        keys = list(set([tag_map[x][tag_map[x].index("-") + 1:].lower() for x in tag_map if x != 0]))
    except:
        keys = list(set([tag_map[x].lower() for x in tag_map if x != 0]))
    return keys

def get_tag_map(data_type):
    if data_type == 'conllpp' or data_type == 'conll2003':
        tag_map = {
            0: 'O',
            1: 'B-person',
            2: 'I-person',
            3: 'B-organization',
            4: 'I-organization',
            5: 'B-location',
            6: 'I-location',
            7: 'B-miscellaneous',
            8: 'I-miscellaneous'
        }
    elif data_type == "WNUT2017":
        tag_map = {
            0: "O",
            1: "B-corporation",
            2: "I-corporation",
            3: "B-creative-work",
            4: "I-creative-work",
            5: "B-group",
            6: "I-group",
            7: "B-location",
            8: "I-location",
            9: "B-person",
            10: "I-person",
            11: "B-product",
            12: "I-product"
        }
    elif data_type == "JNLPBA" or data_type == "BioNER":
        tag_map = {
            0: "O",
            1: "B-DNA",
            2: "I-DNA",
            3: "B-protein",
            4: "I-protein",
            5: "B-cell_type",
            6: "I-cell_type",
            7: "B-cell_line",
            8: "I-cell_line",
            9: "B-RNA",
            10: "I-RNA"
        }
    elif data_type == "ontonotes5":
        tag_map = {
            0: "O",
            1: "B-CARDINAL",
            2: "B-DATE",
            3: "I-DATE",
            4: "B-PERSON",
            5: "I-PERSON",
            6: "B-NORP",
            7: "B-GPE",
            8: "I-GPE",
            9: "B-LAW",
            10: "I-LAW",
            11: "B-ORG",
            12: "I-ORG", 
            13: "B-PERCENT",
            14: "I-PERCENT", 
            15: "B-ORDINAL", 
            16: "B-MONEY", 
            17: "I-MONEY", 
            18: "B-WORK_OF_ART", 
            19: "I-WORK_OF_ART", 
            20: "B-FAC", 
            21: "B-TIME", 
            22: "I-CARDINAL", 
            23: "B-LOC", 
            24: "B-QUANTITY", 
            25: "I-QUANTITY", 
            26: "I-NORP", 
            27: "I-LOC", 
            28: "B-PRODUCT", 
            29: "I-TIME", 
            30: "B-EVENT",
            31: "I-EVENT",
            32: "I-FAC",
            33: "B-LANGUAGE",
            34: "I-PRODUCT",
            35: "I-ORDINAL",
            36: "I-LANGUAGE"
        }
    elif data_type == 'my_data':
        tag_map = {
            0: 'O',
            1: 'B-PRODUCT',
            2: 'I-PRODUCT',
            3: 'B-GENERAL',
            4: 'I-GENERAL',
            5: 'B-SERVICE',
            6: 'I-SERVICE',
            7: 'B-PRODUCT FEATURE',
            8: 'I-PRODUCT FEATURE',
            9: 'B-PRODUCT USAGE',
            10: 'I-PRODUCT USAGE',
            11: 'B-PRODUCT DESIGN',
            12: 'I-PRODUCT DESIGN',
            13: 'B-PRODUCT QUALITY',
            14: 'I-PRODUCT QUALITY',
            15: 'B-PRICE',
            16: 'I-PRICE',
            17: 'B-DELIVERY',
            18: 'I-DELIVERY',

        }
    else:
        tag_map = {
            0: 'O', 
            1: 'art', 
            2: 'building', 
            3: 'event', 
            4: 'location', 
            5: 'organization', 
            6: 'other', 
            7: 'person', 
            8: 'product'
        }
    return tag_map

def get_entity_type_desc(data_type):
    if data_type == 'conllpp' or data_type == 'conll2003':
        entity_type_desc = {
            "person": 'Names of people.',
            'organization': 'Companies, agencies, institutions, etc.',
            'location': 'Names that are locations.',
            'miscellaneous': 'Names of miscellaneous entities that do not belong to person, organization and location.'
        }
    elif data_type == "WNUT2017":
        entity_type_desc = {
            "person": "Names of people (e.g. Virginia Wade).",
            "location": "Names that are locations (e.g. France), including GPE, facility.",
            "corporation": "Names of corporations (e.g. Google), tangible goods, or well-defined services.",
            "product": "Name of products (e.g. iPhone), subsuming music band, sports team, and non-corporate organisations.",
            "creative-work": "Names of creative works (e.g. Bohemian Rhapsody), song, movie, book and so on.",
            "group": "Names of groups (e.g. Nirvana, San Diego Padres), subsuming music band, sports team, and non-corporate organisations."
        }
    elif data_type == "JNLPBA" or data_type == "BioNER":
        entity_type_desc = {
            "dna": "DNA, short for deoxyribonucleic acid, is the molecule that contains the genetic code of organisms.",
            "protein": "Proteins are polymer chains made of amino acids linked together by peptide bonds.",
            "cell_type": "A cell type is a classification used to identify cells that share morphological or phenotypical features.",
            "cell_line": "Cell line is a general term that applies to a defined population of cells that can be maintained in culture for an extended period of time, retaining stability of certain phenotypes and functions.",
            "rna": "Ribonucleic acid (RNA) is a molecule that is present in the majority of living organisms and viruses."
        }
    elif data_type == 'ontonotes5':
        entity_type_desc = {
            "person": "People, including fictional.",
            "norp": "Nationalities or religious or political groups.",
            "fac": "Buildings, airports, highways, bridges, etc.",
            "org": "Companies, agencies, institutions, etc.",
            "gpe": "Countries, cities, states.",
            "loc": "Non-GPE locations, mountain ranges, bodies of water.",
            "product": "V ehicles, weapons, foods, etc. (Not services).",
            "event": "Named hurricanes, battles, wars, sports events, etc.",
            "work_of_art": "Titles of books, songs, etc.",
            "law": "Named documents made into laws.",
            "language": "Any named language.",
            "date": "Absolute or relative dates or periods.",
            "time": "Times smaller than a day.",
            "percent": 'Percentage (including "%").',
            "money": "Monetary values, including unit.",
            "quantity": "Measurements, as of weight or distance.",
            "ordinal": '"first", "second".',
            "cardinal": "Numerals that do not fall under another type."
        }
    elif data_type == 'my_data':
        entity_type_desc = {
            "general": "Những câu thuộc chủ đề chung chung, chứa các aspect ngầm",
            "product": "Những câu thuộc chủ đề liên quan đến sản phẩm nói chung nhưng không rõ ràng về phía cạnh nào",
            "service": "Những câu có chủ đề liên quan tới dịch vụ nói chung , thái độ của nhân viên , các chương trình đặc biệt",
            "delivery": "Những câu có liên quan đến giao hàng , đóng gói , vận chuyển",
            "price": "Những câu có liên quan đến giá cả của sản phẩm",
            "product feature" : "Những câu nói về những đặc trưng tự nhiên , đặc điểm vốn có của sản phẩm",
            "product usage" : "Những câu nói về công dụng của sản phẩm , cảm nhận trong quá trình sử dụng sản phẩm",
            "product design" : "Những câu liên quan đến bao bì , màu săc , thiết kế của sản phẩm",
            "product quality" : "Những câu liên quan đến chất lượng của sản phẩm , độ bền , độ hoàn thiện của sản phẩm"
        }

    return entity_type_desc