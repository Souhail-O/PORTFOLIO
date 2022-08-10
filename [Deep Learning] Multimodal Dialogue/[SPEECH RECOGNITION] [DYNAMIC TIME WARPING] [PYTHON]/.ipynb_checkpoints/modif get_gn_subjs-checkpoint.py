# Dictionnaire de mapping entre articles de base "articles[X]" et article nettoyé doc.text
dct_mapping = {elt[1]: elt[0] for elt in needleman_wunsch(articles[0], doc.text) if elt[0] is not None and elt[1] is not None}


def get_gn_subjs(self, doc):
        """
        Extraire l'ensemble des groupes nominaux sujets (non-pronominaux) qui sont des entités ['GPE', 'PERSON', 'ORG', 'NORP'] et les index de début et de fin
        :param doc:
        :return:
        """
        np_list_subj = []
        gn_subj_idx_clean = []
        gn_subj_idx_origin = []

        for word in doc:
            if word.dep_ == 'nsubj' and word.pos_ not in ['PRON']:
                word_subtree = [str(elt) for elt in word.subtree if str(elt) is not '\n']
                flag = False
                for elt in word_subtree:
                    flag = flag or elt.ent_type_ in ['GPE', 'PERSON', 'ORG', 'NORP']
                if flag:
                    np_list_subj.append(word_subtree)
                    word_index = [elt.idx for elt in word.subtree if str(elt) is not '\n']
                    word_len = [len(elt) for elt in word.subtree]
                    idx_clean = [word_index[0], word_index[-1] + word_len[-1]]
                    idx_origin = [ dct_mapping[idx[0]], dct_mapping[idx[1]-1] ]
                    gn_subj_idx_clean.append(idx_clean)
                    gn_subj_idx_origin.append(idx_origin)

        # reconcatene en liste de string
        gn_subj = [" ".join([str(elt) for elt in GN]).strip() for GN in np_list_subj]
        gn_subj = list(dict.fromkeys(gn_subj))

        return gn_subj, gn_subj_idx_clean, gn_subj_idx_origin