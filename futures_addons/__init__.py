# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 14:53:08 2017

@author: cedric lacrambe <cedric.lacrambe@gmail.com>
"""

#### imports
import os
import math
from concurrent import futures
from functools import partial
import typing
import types
import atexit
import lazy_object_proxy
import weakref
import queue
import threading
import time
import logging
name = "futures_addons"
def buffer_generator(iterator, size=1024 ,delai=0.01  ):
    q=queue.Queue(maxsize=size)
    def ent(iterator,q):
        for i in iterator:
            q.put(i)
    partial
    t=threading.Thread(target=partial(ent,iterator,q))
    t.start()
    while t.is_alive() or not  q.empty() :
        try:
            yield q.get(timeout=delai)
        except queue.Empty :
            pass

class execution_diferee:
    """
    decorateur
    execute la fonction de maniere asynchrone
    retourne un lazy_object_proxy
    """
    def __init__(self, func:typing.Callable[...,typing.Any]=NotImplemented,\
                 executor=None,nom=None,nb_thread=0):
        """
        __init__(self, func:typing.Callable[...,typing.Any]=NotImplemented,\
                 executor=None,nom=None):
        func: fonction a appeler
        executor: futures.executor deja existant
          sinon nouveau futures.ThreadPoolExecutor surcpu_count()*1.2+1 threads
        nom: nom transmis a executor, initialisé à func.__name__

        proprietés:
            fut: liste des futures
            executor: futures.executor de l'init ou futures.ThreadPoolExecutor
            fonction: fonction appelée

        """
        self.fut=[]
        if func is not  NotImplemented and nom is None:
            if nom is None:
                nom=func.__name__
            if func.__doc__ is not None:
                try:
                    doc=self.__doc__+"\naide de la fonction originale\n"+func.__doc__
                    self.__doc__=doc
                except:
                    pass
            self.__wrapped__ =func
        if nom is None:
            nom=str(self)

        self.nom=nom
        self.fonction:typing.Callable=func
        self.executor_init(executor,nb_thread)




    def executor_init(self,executor=None,nb_thread=0):
        if executor is None:
            if nb_thread==0:
                nb_thread=math.floor(os.cpu_count() *1.2)+1
            executor=futures.ThreadPoolExecutor(nb_thread,self.nom+'_executor')
        self.executor=executor
        fin_executor=partial(futures.ThreadPoolExecutor.shutdown,executor)
        weakref.finalize(self,fin_executor)
        atexit.register(fin_executor)
        fin=weakref.WeakMethod(self.terminer)
        #garantir d'attendre les taches en cours
        weakref.finalize(self,fin)
        atexit.register(fin)


    def __del__(self):
#            print("destructeur",self)
            self.terminer()
    def terminer(self,*args):
        """
        appelé a la destruction de l'objet
        """
        encours=[f for f in self.fut if not f.done()]
        if len(encours)>0:
            logging.debug("arret des taches en cours pour : %s",str(self.nom))

#            logging.debug("taches",[f for f in self.fut if not f.done()])
            for i in futures.as_completed(encours):
                try:
                    res=i.result()
                    if res is not None:
                        logging.debug(str(res))
                except:
                    logging.exception(self.nom)


        self.fut.clear()
        self.executor.shutdown()



    def   __call__(self, *args, **kwargs):
        if self.fonction is  NotImplemented :
            if callable(args[0]):
                self.fonction=args[0]
                if args[0].__doc__ is not None and self.__doc__ is not None:
                    doc=self.__doc__
                    doc+="\naide de la fonction originale\n"
                    doc+=     args[0].__doc__
                    self.__doc_=doc
                self.__wrapped__ =args[0]
                return self
            else:
                raise NotImplementedError
        futur=self.executor.submit(self.fonction, *args, **kwargs)
        self.fut.append(futur)
#        return  future_proxy(futur)

        factory_proxy=partial(futures.Future.result,futur)
        return lazy_object_proxy.Proxy(factory_proxy)

class execution_diferee_global(execution_diferee):
    global_executor=None
    def executor_init(self,executor=None,nb_thread=0):
        if executor is None:
            if self.global_executor is None:
                if nb_thread==0:
                    nb_thread=math.floor(os.cpu_count() *1.2)+1
                executor=futures.ThreadPoolExecutor(nb_thread,
                                                'execution_differee_executor')
                self.global_executor=executor
                self.executor=executor
                fin_executor=partial(futures.ThreadPoolExecutor.shutdown,executor)
                atexit.register(fin_executor)

            else:
                   self.executor=self.global_executor
        else:
            self.executor=executor

    def terminer(self,*args):
        pass





def map_as_completed(fonction:typing.Callable,\
                    liste:typing.Iterable[typing.Iterable]\
                    ,executor=None,timeout=None        ):
    """
    map_as_completed(fonction:typing.Callable,\
                    liste:typing.Iterable[typing.Iterable]\
                    ,executor=None,timeout=None        ):
    comme map prent une fonction et une liste de parametresretourne un iterateur
    iterateur qui renvoie les resultats à mesure qu'ils sont completés
    executor
    """
    if executor is None:
        executor=futures.ThreadPoolExecutor(16,fonction.__qualname__ )
    futurs=[]
    for i in liste:
        futurs.append( executor.submit(fonction,*i))
    for fut in futures.as_completed( futurs,timeout):
        yield fut.result()

def ensure_end_method(obj,func,*args):
    func=weakref.WeakMethod(func)
    weakref.finalize(obj,func,*args)




def test():
    """
    >>> test()
    [  test.<locals>.classe_test(0,t) ,   test.<locals>.classe_test(1,t) ,   test.<locals>.classe_test(2,t) ,   test.<locals>.classe_test(3,t) ,   test.<locals>.classe_test(4,t) ]
    """
    class classe_test:
         def __init__(self,ident , contenu=None):
             self.ident=ident
             self.contenu=contenu
         def __repr__ (self):
             return "  {}({},{}) ".format(self. __class__ .__qualname__, self.ident,self.contenu)
    @execution_diferee
    def fontion_test(ident=None):
        return classe_test(ident,"t")
    @execution_diferee
    def fontion_test_boucle(n=20,t=0.01):
        for i in range(n):
            time.sleep(t)
    print("debut")
    liste=[fontion_test(i) for i in range(2)]+[fontion_test_boucle()]
    r=fontion_test,fontion_test_boucle
    w=weakref.ref(fontion_test),weakref.ref(fontion_test_boucle)

    print(liste)

    return r,w,liste


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s : %(message)s',\
                    level="DEBUG",datefmt='%d-%m-%Y %Hh%Mm%S')
    r,w,liste=test()
    print( r,w)
    del r
    print( w)




