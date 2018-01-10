if __name__ == '__main__':
    import parser as Parser
    # import html2text
else:
    from . import parser as Parser
import signal
import sys
import requests

def signal_handler(signal, frame):
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# base URL on which the MMT server runs
MMT_BASE_URL = 'http://localhost:9000/'

# MMT server extension that is used
MMT_SERVER_EXTENSION = 'interview'

class MMTShell():
    def __init__(self):
        # set server Extension
        self.extension = ':'+MMT_SERVER_EXTENSION+'/'

        # set default URI prefix
        self.URI_prefix = 'http://mathhub.info/'

        # the current theory or view
        self.currentScope = None

        # set default MMT namespace
        self.MMT_namespace = 'MitM/smglom/calculus'

        # set default meta theory
        self.metaTheory = 'http://cds.omdoc.org/urtheories?LF'


    # this is mainly for debugging purposes as of now but should be
    # extended with actual functionality to send requests from the shell
    # TODO ask how to decode HTML into plain text
    def handleInputFromShell(self, input):
        parsedInput = Parser.splitInput(input)
        if parsedInput['error'] == True:
            pass
            # return html2text.html2text(parsedInput['message'])

        elif parsedInput['ShellAction'] == 'show namespace':
            return self.MMT_namespace

        elif parsedInput['ShellAction'] == 'show metaTheory':
            return self.metaTheory

        elif parsedInput['ShellAction'] == 'show scope':
            return self.currentScope

        elif parsedInput['ShellAction'] == 'set namespace':
            self.set_MMT_Namespace(parsedInput['data'][0])
            return 'set namespace to '+ self.MMT_namespace

        elif parsedInput['ShellAction'] == 'set metaTheory':
            self.set_MMT_metaTheory(parsedInput['data'][0])
            return 'set metaTheory to '+ self.metaTheory

        elif parsedInput['ShellAction'] == 'create theory':
            self.set_currentScope(parsedInput['data'][0])
            return self.create_theory_URL(parsedInput['data'][0])

        elif parsedInput['ShellAction'] == 'create view':
            self.set_currentScope(parsedInput['data'][0])
            return self.create_view_URL(parsedInput['data'][0],parsedInput['data'][1],parsedInput['data'][2])

        elif parsedInput['ShellAction'] == 'add term':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            return self.add_term_URL(parsedInput['data'][0],theoryName)

        elif parsedInput['ShellAction'] == 'add declaration':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            return self.add_declaration_URL(parsedInput['data'][0],theoryName)
        else:
            return 'Something went seriously wrong!'



    # TODO it would probably be wise to move the requests for each input into a
    # separate method to make things more flexible
    def handleInputFromKernel(self, input):
        parsedInput = Parser.splitInput(input)
        if parsedInput['error'] == True:
            return self.get_display_data(parsedInput['message'])

        elif parsedInput['ShellAction'] == 'show namespace':
            return self.get_display_data(self.MMT_namespace)

        elif parsedInput['ShellAction'] == 'show metaTheory':
            return self.get_display_data(self.metaTheory)

        elif parsedInput['ShellAction'] == 'show scope':
            scope = self.currentScope
            if scope == None:
                scope = 'None'
            return self.get_display_data(scope)

        elif parsedInput['ShellAction'] == 'set namespace':
            self.set_MMT_Namespace(parsedInput['data'][0])
            return self.get_display_data('set namespace to '+ self.MMT_namespace)

        elif parsedInput['ShellAction'] == 'set metaTheory':
            self.set_MMT_metaTheory(parsedInput['data'][0])
            return self.get_display_data('set metaTheory to '+ self.metaTheory)

        elif parsedInput['ShellAction'] == 'create theory':
            self.set_currentScope(parsedInput['data'][0])
            URL = self.create_theory_URL(parsedInput['data'][0])
            return self.get_display_data(requests.get(URL).text)


        elif parsedInput['ShellAction'] == 'create view':
            self.set_currentScope(parsedInput['data'][0])
            URL = self.create_view_URL(parsedInput['data'][0],parsedInput['data'][1],parsedInput['data'][2])
            return self.get_display_data(requests.get(URL).text)

        elif parsedInput['ShellAction'] == 'add term':
            termName = parsedInput['data'][0]
            termContent = parsedInput['data'][1]
            theoryName = parsedInput['data'][2]
            if theoryName == None:
                theoryName = self.currentScope
            URL = self.add_term_URL(parsedInput['data'][0],theoryName)

            term = termName + ':' + termContent
            return self.get_display_data(self.http_request(URL,term).text)

        elif parsedInput['ShellAction'] == 'add declaration':
            declarationName = parsedInput['data'][0]
            declarationContent = parsedInput['data'][1]
            theoryName = parsedInput['data'][2]
            if theoryName == None:
                theoryName = self.currentScope
            URL = self.add_declaration_URL(parsedInput['data'][0],theoryName)

            declaration = declarationName+':'+ declarationContent
            # TODO add content here and in the add term case
            # ask Theresa what the "content" is and how the user enters it
            # remember to add the declaration delimiter after the content
            return self.get_display_data(self.http_request(URL,declaration).text)
        else:
            return 'Something went seriously wrong!'

    def create_theory_URL(self, theoryName):
        return MMT_BASE_URL + self.extension + 'new?theory=' + self.get_path(theoryName) + '&meta=' + self.metaTheory

    def create_view_URL(self, viewName, fromTheory, toTheory):
        return MMT_BASE_URL + self.extension + 'new?view=' + self.get_path(viewName) + '&from=' + self.get_path(fromTheory)+ '&to=' + self.get_path(toTheory)

    def add_term_URL(self,termName,theoryName):
        return MMT_BASE_URL + self.extension +'new?term=' +termName + '&cont=' + self.get_path(theoryName)

    def add_declaration_URL(self,declarationName,theoryName):
        return MMT_BASE_URL + self.extension +'new?decl=' +declarationName + '&cont=' + self.get_path(theoryName)


    # returns the MMT path / URI for a theory or view
    def get_path(self,name):
        return self.URI_prefix + self.MMT_namespace + '?' + name

    def set_currentScope(self,scope):
        self.currentScope = scope

    def set_MMT_Namespace(self, namespace):
        self.MMT_namespace = namespace

    def set_MMT_metaTheory(self,metaTheory):
        self.metaTheory = metaTheory

    def get_display_data(self,message):
        return {
        'data': {
            'text/html':  message
        },
         'metadata': {},
         'transient': {},
        }

    def http_request(self, URL, data=None):
        # print(URL) if self.debugprint else 0
        try:
            if data:
                session = requests.Session()
                adapter = requests.adapters.HTTPAdapter()
                session.mount('https://', adapter)
                session.mount('http://', adapter)
                binary_data = data.encode('UTF-8')
                # print('\n' + str(data)) if self.debugprint else 0
                headers = {'content-type': 'application/json',
                            'content-encoding': 'UTF-8'}
                return session.post(URL, data=binary_data, headers=headers, stream=True)
            else:
                return requests.get(URL)
        except ConnectionError as error: #this seems to never be called
            print(error)
            print("Are you sure the mmt server is running?")
            raise SystemExit
        if req.text.startswith('<'):
            root = etree.fromstring(req.text)
            if root is not None:
                printElement(root)
        if req.status_code == 200:
            return True
        if not req.text.startswith('<'):
            print(req.text)
        return (False, req.text)

    def add_dd(string):
        return string + "❙"

if __name__ == '__main__':
    shell = MMTShell()
    while(True):
        x = input()
        if x == 'q':
            break
        result = shell.handleInputFromShell(x)
        print(result)
