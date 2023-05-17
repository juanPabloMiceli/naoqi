from workspace.utils.logger_factory import LoggerFactory
from threading import Thread
import numpy as np

class Automata(Thread):
    def __init__(self,module_list,memory,verbose=True):
        super(Automata,self).__init__()

        self.LOGGER = LoggerFactory.get_logger("AUTOMATA")
        self._controllable_events = []

        self._map = {}
        self._map_controllable_to_module(module_list)
        self._memory = memory

        self._index = 0
        self._not_exit = 1
        self._set_automata = False
        self._verbose = verbose

    def add_module(self,module):
        self._map_controllable_to_module([module])

        for state in self._states:
            for elem in state:
                if elem[0] in self._controllable_events:
                    elem[1] = 'C'

    '''
    Arranca a correr en un thread independiente cuando hacemos
    automata.start().
    Se encarga de generar los eventos controlables si estamos en un estado con
    eventos controlables y de procesar los eventos entrantes a la cola
    '''
    def run(self):
        self.LOGGER.info("Automata started")
        while (self._not_exit):
            self.LOGGER.info("Thread loop")
            #Stops when the only thing left to do is wait for the environment
            self._generate_controllables()
            if (not self._not_exit):
                break

            #Wait for the environment
            event = self._memory.get_message()
            self._process_event(event)

    def _exit_routine(self):
        while (self._memory.messages_left() > 0):
            self._memory.get_message()

    '''
    Agarra la lista de controlables que expone cada modulo de la lista
    'module_list'.
    In:
    * Lista de modulos
    Out:
    * self._controllable_events va a ser una lista de strings con todos los
    eventos controlables
    * self._map va a ser una diccionario cuya clave va a ser uno de estos
    strings de eventos controlables y el valor va a ser la funcion del evento
    expuesta por el modulo.
    '''
    def _map_controllable_to_module(self,module_list):
        for module in module_list:
            for controllable in module.controllables:
                self._controllable_events.append(controllable)
                self._map[controllable] = getattr(module,controllable)

    def _generate_controllables(self):
        controllable_found = 1
        states = self._states
        while (controllable_found):
            self.LOGGER.info("Inside controllable_found")
            while(self._memory.messages_left() > 0):
                self.LOGGER.info("Trying to empty queue")
                event = self._memory.get_message()
                self._process_event(event)

            #Search for controllables
            controllable_found = 0
            list_contr = []
            list_elem = []
            for elem in states[self._index]:
                self.LOGGER.info("En estado {}".format(elem))
                if (elem[1] == 'C'):
                    controllable_found = 1
                    list_contr.append(elem[0])
                    list_elem.append(elem)

            if controllable_found:
                #index = self._choice_selector.select_controllable(list_contr,self._index)
                index = 0
                self._process_event(list_contr[index],controllable=True,element=list_elem[index])
        return
    '''
    Si me llega un evento que no conozco exploto
    '''
    def _error_routine(self,event):
        print("EVENT " + event + " NOT FOUND")
        self._map['rtl']()
        self._not_exit = 0
        self._exit_routine()

    def _process_event(self,event,controllable=False,element=None):
        if (self._verbose):
            print(event)
        if (event == 'exit'):
            self._not_exit = 0
            self._exit_routine()
            return

        if not controllable:
            for elem in self._states[self._index]:
                if(elem[0] == event):
                    self._index = int(elem[2])
                    return True #Accepted
        else:
            elem = element
            map_obj = self._map
            self._index = int(elem[2])
            #Call controllable
            try:
                values = elem[0].split('[')
                if (len(values) == 1):
                    event = map_obj[elem[0]]()
                elif (len(values) == 2):
                    event = map_obj[values[0]]((values[1])[:-1])
                else:
                    print(elem[0] + " too many arguments")
            except KeyError:
                print(elem[0] + " action not callable")
                return False

            if (event != None):
                self._process_event(event)
            return True

        self._error_routine(event)
        return False #Not Accepted

    def load_automata_from_file(self,automata_file):
        filename = automata_file

        file = open(filename,'r')
        automata_data = file.read()
        file.close()

        self.load_automata(automata_data)

    '''
    Dado un automata generado con la herramienta mtsa (window  'Transitions'), clonable en este link
    https://bitbucket.org/lnahabedian/mtsa/src/master/.
    Parseamos el string y conseguimos un array de transiciones del tipo:

        self._states = np.array([
            [['accion','C',1], ['evento', 'A', 0]], #0
            [['evento','A',0], ['accion', 'C', 1]] #1
        ])

    'accion' o 'evento' es el identificador de la accion o el evento, puede ser
    practicamente cualquier string.

    'C' indica que es una transicion controlable y 'A' indica que es una
    transicion dada por el evento de un sensor (no controlable).

    El numero de la tercer posicion del array indica a que estado transiciona.

    Podemos saber de que estado transicion preguntando en que posicion del
    array principal se encuentra, arriba se marca con #n.
    '''
    def load_automata(self,automata_data):
        lines = automata_data.splitlines()
        states_size = int(lines[3].strip())
        states = [[]]*states_size

        analysing_state = False
        num_state = 0
        for i in range(6,len(lines)):
            line = lines[i].strip()

            if(analysing_state == False):
                if (line[0] == 'Q'):
                    analysing_state = True
                    aux_vec = []
            if(analysing_state == True):
                    aux_str = ''
                    many_events = False
                    action_set = False
                    for char in line:
                        if (char == '='):
                            num_state = int(aux_str[1:].strip())
                            continue

                        if (char in ['(','{','|']):
                            aux_str = ''
                            continue

                        if (char == '}'):
                            many_events = True
                            action = aux_str
                            action_set = True
                            continue

                        if (many_events == False and char == '-'):
                            action = aux_str
                            action_set = True
                            continue

                        if (action_set == True):
                            if (char == 'Q'):
                                aux_str = ''
                                continue

                        if (char == ')'):
                            num_next_state = int(aux_str.strip())
                            analysing_state = False
                            break

                        aux_str = aux_str + char

                    if(analysing_state == True):
                        num_next_state = int(aux_str.strip())

                    if (many_events == True):
                        aux_lista = np.array([])
                        aux_str = ''
                        for j in range(len(action)):
                            if (action[j] == ','):
                                aux_lista = np.append(aux_lista,aux_str)
                                aux_str = ''
                                continue
                            aux_str += action[j]
                            if (j == len(action)-1):
                                aux_lista = np.append(aux_lista,aux_str)
                        action = aux_lista
                    else:
                        action = [action]

                    for accion in action:
                        accion = accion.strip()
                        values = accion.split('[')
                        if (values[0] in self._controllable_events):
                            aux_var = 'C'
                        else:
                            aux_var = 'A'
                        aux_vec.append([accion,aux_var,num_next_state])

                    if(analysing_state == False):
                        states[num_state] = aux_vec

        print("\n\n\nEstados: {} \n\n\n".format(states))
        self._states = states
        return
