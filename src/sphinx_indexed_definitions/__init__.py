from sphinx.application import Sphinx
from sphinx_proof.proof_type import DefinitionDirective, TheoremDirective, LemmaDirective, ConjectureDirective, CorollaryDirective, PropositionDirective, NotationDirective
from pathlib import PurePosixPath
import os
import re
from docutils import nodes
from sphinx.environment.adapters.indexentries import IndexEntries
import yaml

SUPPORTED_NODES = ['strong','emphasis','literal']
DEFAULT_NODES = ['strong','emphasis']
CAPITAL_WORDS = list({'Cartesian','Markov','Euler','Neumann','Newton','Gauss','Lagrange','Hilbert','Frobenius','Navier','Stokes','Laplace','Cauchy','Erdős','Ramanujan',
                      'Kolmogorov','Darcy','Archimedes','Chebychev','Castigliano','Taylor','Maclaurin','Macaulay','Mohr','Jensens','Muller','Breslau','Bernoulli',
                      'Maxwell','Einstein','Froud','Reynolds','Betti','Rayleigh','Ohm','Volt','Ampère','Tesla','Curie','Turing','Murphy','Avogrado','Planck','Feynman',
                      'Nash','Bequerel','Pascal','Joule','Kelvin','Lenz','Celsius','Fahrenheit','Snell','Watt','Réaumur','Kelvin','Lenz','Celsius','Fahrenheit','Snell',
                      'Boole','Dirichlet','Euclid','Leibniz','Benford','Boyer','Dijkstra','Huygens','Lambert','Poisson','Weierstrass','Abel','Descartes','Fibonacci',
                      'Hôpital','Poincaré','Volterra','Lotka','Cramer','Schwarz','Cayley','Hamilton','Perron'})

class IndexedDefinitionDirective(DefinitionDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = DefinitionDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        # now find all indicated nodes and the (optional) title
        stuff_to_index = set()
        titles_to_index = set()
        # find out if a title has been set (and has to be indexed)
        if self.env.config.sphinx_indexed_defs_index_titles:
            if len(self.arguments) != 0:
                title = self.arguments[0]
                # Check if a footnote is inside the title, and if so, remove it from the string to be indexed
                # Assume [^ ] pattern for footnotes in the title
                footnotes = re.findall(r"\[\^.*?\]", title)
                for note in footnotes:
                    title = title.replace(note, "")
                if self.env.config.sphinx_indexed_defs_lowercase_indices:
                    new_string = title.lower()
                    new_math = re.findall(r"\$(.*?)\$", new_string)
                    old_math = re.findall(r"\$(.*?)\$", title)
                    for eeeee,mathe in enumerate(new_math):
                        new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$")
                    for word in self.env.config.sphinx_indexed_defs_capital_words:
                        new_string = new_string.replace(f"{word.lower()}",f"{word}")
                    title = new_string.strip()
                stuff_to_index.add(title)
                titles_to_index.add(title)
        for typ in self.env.config.sphinx_indexed_defs_indexed_nodes:
            assert typ in SUPPORTED_NODES, f"the node {typ} is not supported"
            list_of_nodes = def_nodes[0][1]
            for def_node in list_of_nodes:
                cls = eval("nodes."+typ)
                typ_nodes = def_node.findall(cls)
                for node in typ_nodes:
                    node_string = node.__str__()
                    node_string = node_string.replace(f"<{typ}>","").strip()
                    node_string = node_string.replace(f"</{typ}>","").strip()
                    node_string = node_string.replace(f"<{typ}/>","").strip()
                    node_string = node_string.replace("<math>","$").strip()
                    node_string = node_string.replace("</math>","$").strip()
                    # check if a footnote is inside the node, and if so, remove it from the string to be indexed
                    footnotes = list(node.findall(nodes.footnote_reference))
                    if footnotes:
                        for note in footnotes:
                            node_string = node_string.replace(note.__str__(),"")
                    if self.env.config.sphinx_indexed_defs_lowercase_indices:
                        new_string = node_string.lower().strip()
                        new_math = re.findall(r"\$(.*?)\$", new_string)
                        old_math = re.findall(r"\$(.*?)\$", node_string)
                        for eeeee,mathe in enumerate(new_math):
                            new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$").strip()
                        for word in self.env.config.sphinx_indexed_defs_capital_words:
                            new_string = new_string.replace(f"{word.lower()}",f"{word}").strip()
                        node_string = new_string.strip()

                    if self.env.config.sphinx_indexed_defs_remove_brackets:
                        if "(" not in node_string:
                            # check for weird references
                            if node_string in titles_to_index:
                                # remove from titles_to_index, since it should be indexed as a term, not as a title
                                titles_to_index.remove(node_string)
                            if "classes" not in node_string:
                                stuff_to_index.add(node_string)
                            elif "xref" not in node_string:
                                stuff_to_index.add(node_string)
                        else:    
                            bracketted = re.findall(r"\((.*?)\)", node_string)
                            node_string_none = node_string.strip()
                            node_string_all = node_string.strip()
                            for word in bracketted:
                                node_string_none = node_string_none.replace(f"({word})","").strip()
                                node_string_all = node_string_all.replace(f"({word})",f"{word}").strip()
                            # check for weird references
                            if node_string_all in titles_to_index:
                                # remove from titles_to_index, since it should be indexed as a term, not as a title
                                titles_to_index.remove(node_string_all)
                            if "classes" not in node_string_all:
                                stuff_to_index.add(node_string_all)
                            elif "xref" not in node_string_all:
                                stuff_to_index.add(node_string_all)
                            # check for weird references
                            if node_string_none in titles_to_index:
                                # remove from titles_to_index, since it should be indexed as a term, not as a title
                                titles_to_index.remove(node_string_none)
                            if "classes" not in node_string_none:
                                stuff_to_index.add(node_string_none)
                            elif "xref" not in node_string_none:
                                stuff_to_index.add(node_string_none)
                    else:
                        # check for weird references
                        if node_string in titles_to_index:
                            # remove from titles_to_index, since it should be indexed as a term, not as a title
                            titles_to_index.remove(node_string)
                        if "classes" not in node_string:
                            stuff_to_index.add(node_string)
                        elif "xref" not in node_string:
                            stuff_to_index.add(node_string)

        indexes = ""
        if len(stuff_to_index)>0:
            for index in stuff_to_index:
                # check if the index should be skipped
                skip_index = False
                if index == "":
                    continue
                for regexp in self.env.config.sphinx_indexed_defs_skip_indices:
                    if re.search(regexp,index):
                        skip_index = True
                        break
                if skip_index:
                    continue
                if self.env.config.sphinx_indexed_defs_force_main and index not in titles_to_index:
                    indexes += f"{{index}}`!{index}`"
                else:
                    indexes += f"{{index}}`{index}`"
        start_node = [nodes.raw(None, "<div style=\"overflow:hidden;height:0px;margin:calc(var(--bs-body-font-size)*-0.5);\">", format="html")]
        end_node = [nodes.raw(None, "</div>", format="html")]
        try:
            parsed_indexes = self.parse_text_to_nodes(indexes)
        except:
            parsed_indexes = []
        node_list = start_node + parsed_indexes + end_node + def_nodes

        return node_list

def setup(app: Sphinx):

    app.add_config_value('sphinx_indexed_defs_indexed_nodes',DEFAULT_NODES,'env')
    app.add_config_value('sphinx_indexed_defs_skip_indices',[],'env')
    app.add_config_value('sphinx_indexed_defs_lowercase_indices',True,'env')
    app.add_config_value('sphinx_indexed_defs_index_titles',True,'env')
    app.add_config_value('sphinx_indexed_defs_capital_words',[],'html')
    app.add_config_value('sphinx_indexed_defs_remove_brackets',True,'env')
    app.add_config_value('sphinx_indexed_defs_force_main',True,'env')
    app.add_config_value('sphinx_indexed_defs_index_theorems',True,'env')
    app.add_config_value('sphinx_indexed_defs_index_theorems_terms',False,'env')

    app.connect('builder-inited',parse_config)

    app.setup_extension('sphinx_proof')

    app.add_directive_to_domain('prf','definition',IndexedDefinitionDirective,override=True)
    app.add_directive_to_domain('prf','theorem',IndexedTheoremDirective,override=True)
    app.add_directive_to_domain('prf','lemma',IndexedLemmaDirective,override=True)
    app.add_directive_to_domain('prf','conjecture',IndexedConjectureDirective,override=True)
    app.add_directive_to_domain('prf','corollary',IndexedCorollaryDirective,override=True)
    app.add_directive_to_domain('prf','proposition',IndexedPropositionDirective,override=True)
    app.add_directive_to_domain('prf','notation',IndexedNotationDirective,override=True)

    
    app.connect("builder-inited", lambda app: patch_index(app))

    return {}

def parse_config(app:Sphinx):
    
    capital_words = app.config.sphinx_indexed_defs_capital_words + CAPITAL_WORDS
    app.config.sphinx_indexed_defs_capital_words = list(set(capital_words))

    pass

class IndexedTheoremDirective(TheoremDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = TheoremDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes
    
class IndexedLemmaDirective(LemmaDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = LemmaDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes

class IndexedConjectureDirective(ConjectureDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = ConjectureDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes
    
class IndexedCorollaryDirective(CorollaryDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = CorollaryDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes
    
class IndexedPropositionDirective(PropositionDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = PropositionDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes
    
class IndexedNotationDirective(NotationDirective):

    def run(self):        

        # first the normal parse:
        def_nodes = NotationDirective.run(self)
        # get the classes and do no index stuff if told so.
        classes = self.options.get('class')
        if classes is not None:
            if "skipindexing" in classes:
                return def_nodes
        if self.env.config.sphinx_indexed_defs_index_theorems and not self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_only_title(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems_terms and not self.env.config.sphinx_indexed_defs_index_theorems:
            def_nodes = parse_only_terms(self,def_nodes)
        if self.env.config.sphinx_indexed_defs_index_theorems and self.env.config.sphinx_indexed_defs_index_theorems_terms:
            def_nodes = parse_title_and_terms(self,def_nodes)

        return def_nodes

def parse_only_title(self,def_nodes):
        
    stuff_to_index = set()
    # find out if a title has been set (and has to be indexed)
    if len(self.arguments) != 0:
        title = self.arguments[0]
        # Check if a footnote is inside the title, and if so, remove it from the string to be indexed
        # Assume [^ ] pattern for footnotes in the title
        footnotes = re.findall(r"\[\^.*?\]", title)
        for note in footnotes:
            title = title.replace(note, "")
        if self.env.config.sphinx_indexed_defs_lowercase_indices:
            new_string = title.lower()
            new_math = re.findall(r"\$(.*?)\$", new_string)
            old_math = re.findall(r"\$(.*?)\$", title)
            for eeeee,mathe in enumerate(new_math):
                new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$")
            for word in self.env.config.sphinx_indexed_defs_capital_words:
                new_string = new_string.replace(f"{word.lower()}",f"{word}")
            title = new_string.strip()
        stuff_to_index.add(title)

    indexes = ""
    if len(stuff_to_index)>0:
        for index in stuff_to_index:
            # check if the index should be skipped
            skip_index = False
            if index == "":
                continue
            for regexp in self.env.config.sphinx_indexed_defs_skip_indices:
                if re.search(regexp,index):
                    skip_index = True
                    break
            if skip_index:
                continue
            indexes += f"{{index}}`{index}`"
    start_node = [nodes.raw(None, "<div style=\"overflow:hidden;height:0px;margin:calc(var(--bs-body-font-size)*-0.5);\">", format="html")]
    end_node = [nodes.raw(None, "</div>", format="html")]
    try:
        parsed_indexes = self.parse_text_to_nodes(indexes)
    except:
        parsed_indexes = []
    node_list = start_node + parsed_indexes + end_node + def_nodes

    return node_list

def parse_only_terms(self,def_nodes):

    # now find all indicated nodes and the (optional) title
    stuff_to_index = set()
    for typ in self.env.config.sphinx_indexed_defs_indexed_nodes:
        assert typ in SUPPORTED_NODES, f"the node {typ} is not supported"
        list_of_nodes = def_nodes[0][1]
        for def_node in list_of_nodes:
            cls = eval("nodes."+typ)
            typ_nodes = def_node.findall(cls)
            for node in typ_nodes:
                node_string = node.__str__()
                node_string = node_string.replace(f"<{typ}>","").strip()
                node_string = node_string.replace(f"</{typ}>","").strip()
                node_string = node_string.replace(f"<{typ}/>","").strip()
                node_string = node_string.replace("<math>","$").strip()
                node_string = node_string.replace("</math>","$").strip()
                # check if a footnote is inside the node, and if so, remove it from the string to be indexed
                footnotes = list(node.findall(nodes.footnote_reference))
                if footnotes:
                    for note in footnotes:
                        node_string = node_string.replace(note.__str__(),"")
                if self.env.config.sphinx_indexed_defs_lowercase_indices:
                    new_string = node_string.lower().strip()
                    new_math = re.findall(r"\$(.*?)\$", new_string)
                    old_math = re.findall(r"\$(.*?)\$", node_string)
                    for eeeee,mathe in enumerate(new_math):
                        new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$").strip()
                    for word in self.env.config.sphinx_indexed_defs_capital_words:
                        new_string = new_string.replace(f"{word.lower()}",f"{word}").strip()
                    node_string = new_string.strip()

                if self.env.config.sphinx_indexed_defs_remove_brackets:
                    if "(" not in node_string:
                        # check for weird references
                        if "classes" not in node_string:
                            stuff_to_index.add(node_string)
                        elif "xref" not in node_string:
                            stuff_to_index.add(node_string)
                    else:    
                        bracketted = re.findall(r"\((.*?)\)", node_string)
                        node_string_none = node_string.strip()
                        node_string_all = node_string.strip()
                        for word in bracketted:
                            node_string_none = node_string_none.replace(f"({word})","").strip()
                            node_string_all = node_string_all.replace(f"({word})",f"{word}").strip()
                        # check for weird references
                        if "classes" not in node_string_all:
                            stuff_to_index.add(node_string_all)
                        elif "xref" not in node_string_all:
                            stuff_to_index.add(node_string_all)
                        # check for weird references
                        if "classes" not in node_string_none:
                            stuff_to_index.add(node_string_none)
                        elif "xref" not in node_string_none:
                            stuff_to_index.add(node_string_none)
                else:
                    # check for weird references
                    if "classes" not in node_string:
                        stuff_to_index.add(node_string)
                    elif "xref" not in node_string:
                        stuff_to_index.add(node_string)

    indexes = ""
    if len(stuff_to_index)>0:
        for index in stuff_to_index:
            # check if the index should be skipped
            skip_index = False
            if index == "":
                continue
            for regexp in self.env.config.sphinx_indexed_defs_skip_indices:
                if re.search(regexp,index):
                    skip_index = True
                    break
            if skip_index:
                continue
            if self.env.config.sphinx_indexed_defs_force_main:
                indexes += f"{{index}}`!{index}`"
            else:
                indexes += f"{{index}}`{index}`"
    start_node = [nodes.raw(None, "<div style=\"overflow:hidden;height:0px;margin:calc(var(--bs-body-font-size)*-0.5);\">", format="html")]
    end_node = [nodes.raw(None, "</div>", format="html")]
    try:
        parsed_indexes = self.parse_text_to_nodes(indexes)
    except:
        parsed_indexes = []
    node_list = start_node + parsed_indexes + end_node + def_nodes
    
    return node_list

def parse_title_and_terms(self,def_nodes):
    stuff_to_index = set()
    titles_to_index = set()
    if len(self.arguments) != 0:
        title = self.arguments[0]
        # Check if a footnote is inside the title, and if so, remove it from the string to be indexed
        # Assume [^ ] pattern for footnotes in the title
        footnotes = re.findall(r"\[\^.*?\]", title)
        for note in footnotes:
            title = title.replace(note, "")
        if self.env.config.sphinx_indexed_defs_lowercase_indices:
            new_string = title.lower()
            new_math = re.findall(r"\$(.*?)\$", new_string)
            old_math = re.findall(r"\$(.*?)\$", title)
            for eeeee,mathe in enumerate(new_math):
                new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$")
            for word in self.env.config.sphinx_indexed_defs_capital_words:
                new_string = new_string.replace(f"{word.lower()}",f"{word}")
            title = new_string.strip()
        stuff_to_index.add(title)
        titles_to_index.add(title)
    
    for typ in self.env.config.sphinx_indexed_defs_indexed_nodes:
        assert typ in SUPPORTED_NODES, f"the node {typ} is not supported"
        list_of_nodes = def_nodes[0][1]
        for def_node in list_of_nodes:
            cls = eval("nodes."+typ)
            typ_nodes = def_node.findall(cls)
            for node in typ_nodes:
                node_string = node.__str__()
                node_string = node_string.replace(f"<{typ}>","").strip()
                node_string = node_string.replace(f"</{typ}>","").strip()
                node_string = node_string.replace(f"<{typ}/>","").strip()
                node_string = node_string.replace("<math>","$").strip()
                node_string = node_string.replace("</math>","$").strip()
                # check if a footnote is inside the node, and if so, remove it from the string to be indexed
                footnotes = list(node.findall(nodes.footnote_reference))
                if footnotes:
                    for note in footnotes:
                        node_string = node_string.replace(note.__str__(),"")
                if self.env.config.sphinx_indexed_defs_lowercase_indices:
                    new_string = node_string.lower().strip()
                    new_math = re.findall(r"\$(.*?)\$", new_string)
                    old_math = re.findall(r"\$(.*?)\$", node_string)
                    for eeeee,mathe in enumerate(new_math):
                        new_string = new_string.replace(f"${mathe}$",f"${old_math[eeeee]}$").strip()
                    for word in self.env.config.sphinx_indexed_defs_capital_words:
                        new_string = new_string.replace(f"{word.lower()}",f"{word}").strip()
                    node_string = new_string.strip()

                if self.env.config.sphinx_indexed_defs_remove_brackets:
                    if "(" not in node_string:
                        # check for weird references
                        if node_string in titles_to_index:
                            # remove from titles_to_index, since it should be indexed as a term, not as a title
                            titles_to_index.remove(node_string)
                        if "classes" not in node_string:
                            stuff_to_index.add(node_string)
                        elif "xref" not in node_string:
                            stuff_to_index.add(node_string)
                    else:    
                        bracketted = re.findall(r"\((.*?)\)", node_string)
                        node_string_none = node_string.strip()
                        node_string_all = node_string.strip()
                        for word in bracketted:
                            node_string_none = node_string_none.replace(f"({word})","").strip()
                            node_string_all = node_string_all.replace(f"({word})",f"{word}").strip()
                        # check for weird references
                        if node_string_all in titles_to_index:
                            # remove from titles_to_index, since it should be indexed as a term, not as a title
                            titles_to_index.remove(node_string_all)
                        if "classes" not in node_string_all:
                            stuff_to_index.add(node_string_all)
                        elif "xref" not in node_string_all:
                            stuff_to_index.add(node_string_all)
                        # check for weird references
                        if node_string_none in titles_to_index:
                            # remove from titles_to_index, since it should be indexed as a term, not as a title
                            titles_to_index.remove(node_string_none)
                        if "classes" not in node_string_none:
                            stuff_to_index.add(node_string_none)
                        elif "xref" not in node_string_none:
                            stuff_to_index.add(node_string_none)
                else:
                    # check for weird references
                    if node_string in titles_to_index:
                        # remove from titles_to_index, since it should be indexed as a term, not as a title
                        titles_to_index.remove(node_string)
                    if "classes" not in node_string:
                        stuff_to_index.add(node_string)
                    elif "xref" not in node_string:
                        stuff_to_index.add(node_string)

    indexes = ""
    if len(stuff_to_index)>0:
        for index in stuff_to_index:
            # check if the index should be skipped
            skip_index = False
            if index == "":
                continue
            for regexp in self.env.config.sphinx_indexed_defs_skip_indices:
                if re.search(regexp,index):
                    skip_index = True
                    break
            if skip_index:
                continue
            if self.env.config.sphinx_indexed_defs_force_main and index not in titles_to_index: # do not bold titles, only terms
                indexes += f"{{index}}`!{index}`"
            else:
                indexes += f"{{index}}`{index}`"
    start_node = [nodes.raw(None, "<div style=\"overflow:hidden;height:0px;margin:calc(var(--bs-body-font-size)*-0.5);\">", format="html")]
    end_node = [nodes.raw(None, "</div>", format="html")]
    try:
        parsed_indexes = self.parse_text_to_nodes(indexes)
    except:
        parsed_indexes = []
    node_list = start_node + parsed_indexes + end_node + def_nodes

    return node_list


def patch_index(app):
    env = app.env

    # -----------------------------
    # Build TOC document order
    # -----------------------------
    doc_order = build_doc_order(env)

    # -----------------------------
    # Build anchor positions per doc
    # -----------------------------
    anchor_positions = build_anchor_positions(env)

    # -----------------------------
    # Monkeypatch
    # -----------------------------
    original = IndexEntries.create_index

    def custom_create_index(self, builder, group_entries=True):
        content = original(self, builder, group_entries)

        for _, entries in content:
            for i, (term, (links, subitems, key)) in enumerate(entries):

                def sort_key(link):
                    # Current Sphinx index targets are (main, uri) pairs.
                    _, uri = link

                    if not uri:
                        return (10**9, 10**9)

                    target = uri.split("#", 1)[0]
                    anchor = uri.split("#", 1)[1] if "#" in uri else ""
                    docname = target[:-5] if target.endswith(".html") else target

                    # 1. TOC order
                    doc_pos = doc_order.get(docname, 10**9)

                    # 2. Prefer numeric index anchors when available so same-document
                    # entries follow their source order in the generated index.
                    index_match = re.search(r"index-(\d+)$", anchor)
                    if index_match:
                        anchor_pos = (0, int(index_match.group(1)))
                    else:
                        anchor_map = anchor_positions.get(docname, {})
                        anchor_pos = (1, anchor_map.get(anchor, 10**9))

                    return (doc_pos, anchor_pos)

                links.sort(key=sort_key)

                entries[i] = (term, (links, subitems, key))

        return content

    IndexEntries.create_index = custom_create_index


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def build_doc_order(env):
    """
    Build document order based on the external TOC file order.
    """
    order = {}
    counter = [0]

    def normalize_docname(path):
        if not path:
            return None
        normalized = path.replace("\\", "/")
        return str(PurePosixPath(normalized).with_suffix(""))

    def add_doc(path):
        docname = normalize_docname(path)
        if docname and docname not in order:
            order[docname] = counter[0]
            counter[0] += 1

    def walk_item(item):
        if not isinstance(item, dict):
            return

        add_doc(item.get("file"))

        for key in ("parts", "chapters", "sections"):
            for child in item.get(key, []) or []:
                walk_item(child)

    toc_name = getattr(env.config, "external_toc_path", "_toc.yml")
    toc_path = toc_name if os.path.isabs(toc_name) else os.path.join(env.app.srcdir, toc_name)

    if os.path.exists(toc_path):
        try:
            with open(toc_path, "r", encoding="utf-8") as toc_file:
                toc_data = yaml.safe_load(toc_file) or {}
        except Exception as exc:
            pass
        else:
            add_doc(toc_data.get("root"))
            for part in toc_data.get("parts", []) or []:
                walk_item(part)

    # fallback: include any missing docs
    for doc in env.found_docs:
        if doc not in order:
            order[doc] = counter[0]
            counter[0] += 1

    return order


def build_anchor_positions(env):
    """
    Build approximate top-to-bottom order of anchors per document
    """
    positions = {}

    for docname in env.found_docs:
        try:
            doctree = env.get_doctree(docname)
        except FileNotFoundError:
            continue
        pos = {}
        counter = 0

        for node in doctree.traverse():
            if not isinstance(node, nodes.Element):
                continue
            ids = node.get("ids", [])
            for anchor in ids:
                pos[anchor] = counter
            counter += 1

        positions[docname] = pos

    return positions
