# -*- coding: utf-8 -*-

from contextlib import contextmanager

import System
from System.Runtime.InteropServices import Marshal

import logging


@contextmanager
def autorelease(comobj):
  """COM auto release contextmanager"""
  try:
    yield comobj
  finally:
    Marshal.ReleaseComObject(comobj)



class AutoReleasingComObject(object):
    '''
    Wraps a given ComObject and allows to auto-release all ComObject-instances
    created by accessing attributes/methods of the ComObject.
    
    The AutoReleasingComObject-instance can be used as context-manager, which
    will release all generated ComObjects on exiting the with-context.
    By default, the wrapped ComObject in this AutoReleasingComObject-instance is also released.
    This is configurable by the release_self-parameter.
    '''
    
    def __init__(self, comobj, release_self=True):
        ''' Constructor '''
        # if not type(comobj).__name__ == '__ComObject':
        #     # FIXME: raise ERROR
        #     #raise AttributeError("AutoReleasingComObject expects to wrap a ComObject.")
        #     self._is_comobj = False
        #     pass
        self._is_comobj = (type(comobj).__name__ == '__ComObject')
        self._comobj = comobj
        self._release_self = release_self
        self._accessed_com_attributes = []
        logging.debug("Com-Release: created AutoReleasingComObject %s for %s" % (self, comobj))
    
    
    # Magic methods: https://rszalski.github.io/magicmethods/
    
    
    ##### COMPARISION and OPERATORS #####
    
    def __eq__(self, other):
        ''' Return true if containig ComObject is equal '''
        if isinstance(other, AutoReleasingComObject):
            return self._comobj == other._comobj
        else:
            return self._comobj == other

    def __ne__(self, other):
        ''' Return true if containig ComObject is not equal '''
        if isinstance(other, AutoReleasingComObject):
            return self._comobj != other._comobj
        else:
            return self._comobj != other
    
    # assignment is used with events
    def __iadd__(self, other):
        self._comobj += other
    def __isub__(self, other):
        self._comobj -= other
        
    
    
    ##### CLASS REPRESENTATION #####
    # TODO:
    #def __str__(self):
    #def __repr__(self):
    #def __dir__(self):
    
    
    
    ##### ATTRIBUTE ACCESS #####
    
    def __setattr__(self, attr, value):
        '''
        Only allow to write attributes starting with _
        All other attributes are written to wrapped ComObject
        '''
        if attr[0] == "_":
            super(AutoReleasingComObject, self).__setattr__(attr, value)
        else:
            setattr(self._comobj, attr, value)
    
        
    def __getattr__(self, attr):
        '''
        Provides access to attributes and methods of the ComObject
        If attr is a ComObject, an AutoReleasingComObject-instance will be returned.
        If attr is another value, this value is returned.
        If attr is a method, a wrapper-method will be returned, which will create an AutoReleasingComObject-instance (or return a non-Com-value) after the method-call
        
        The ComObjects which are generated by attribute/method-access are stored.
        All these ComObjects can be released be calling dispose.
        Dispose will go down the AutoReleasingComObject-tree to automatically release all ComObjects accessed in this ComObject-tree.
        '''
        
        # FIXME: hack to allow: .item[1]=xxx
        if attr == 'Item' or attr == 'item':
            return self
        
        value = getattr(self._comobj, attr)
        logging.debug("Com-Release: access to attribute %s" % (attr))
        
        if type(value).__name__ != 'DispCallable':
            # attribute did not return a function
            # create auto-release-object or directly return the value
            return self.create_and_register_auto_release_com_object(value)
            
        else:
            # attribute is actually a function
            # Return wrapper which creates auto-release-object after it has been called.
            # WrappedDispCallable additionally allows array-access to the function, so that
            #   foo.item(1), foo.item[1], foo.item(1,2), foo.item[1,2]
            # all work.
            
            return WrappedDispCallable(self, attr)
            
    
    
    ##### CUSTOM SEQUENCES #####
    #TODO:
    #def __len__(self):
    #def __delitem__(self, key):
    #def __reversed__(self):
    #def __contains__(self, item):
    
    def __getitem__(self, key):
        '''
        If wrapped ComObject is subscriptable, the allow array access.
        ComObject are wrapped as AutoReleasingComObject, before they are returned.
        '''
        if hasattr(self._comobj, 'Item'):
            return_value = self._comobj.Item(key)
            return self.create_and_register_auto_release_com_object(return_value)
            
        else:
            raise TypeError('\'%s\' object is not subscriptable' % type(self._comobj))
        
    
    # FIXME: setting value should also be possible through:  .item[1]=value
    def __setitem__(self, key, value):
        '''
        If wrapped ComObject is subscriptable, the allow array access.
        ComObject are wrapped as AutoReleasingComObject, before they are returned.
        '''
        if hasattr(self._comobj, 'Item'):
            self._comobj[key] = value
            
        else:
            raise TypeError('\'%s\' object is not subscriptable' % type(self._comobj))
        
    
    
    def __iter__(self):
        '''
        If wrapped ComObject is iterable, the return an iterator.
        The iterator will wrap each ComObject as AutoReleasingComObject, before they are returned.
        '''
        if hasattr(self._comobj, 'Item') and hasattr(self._comobj, 'Count'):
            for i in range(self._comobj.Count):
                yield AutoReleasingComObject(self._comobj.Item(i+1))
            
        else:
            raise TypeError('iteration over non-sequence of type %s' % type(self._comobj))
    
    
    
    ##### REFLECTION #####
    #TODO:
    #def __instancecheck__(self, instance):
    #def __subclasscheck__(self, subclass):
    
    
    
    ##### CALLABLE OBJECTS #####
    
    def __call__(self, *args, **kwargs):
        value = self._comobj(*args, **kwargs)
        return self.create_and_register_auto_release_com_object(value)
    
    
    
    ##### CONTEXT MANAGER #####
    
    def __enter__(self):
        '''
        Allow usage as context-manager (with-statement).
        '''
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Allow usage as context-manager (with-statement).
        After exiting, all accessed ComObjects are released.
        By default, the wrapped ComObject in the AutoReleasingComObject-instance is also released.
        This is configurable by the release_self-parameter.
        '''
        self.dispose()
    
    
    
    ##### AutoReleasingComObject Functionality #####
    
    def create_and_register_auto_release_com_object(self, com_obj):
        '''
        creates an AutoReleasingComObject-instance if com_obj is a ComObject,
        or returns the given value
        '''
        if type(com_obj).__name__ == '__ComObject':
            if self._is_comobj:
                auto_release_com_obj = AutoReleasingComObject(com_obj, release_self=True)
                logging.debug("Com-Release: created com-object %s" % (com_obj))
            else:
                # self is no com-Object, but the attribute is. 
                # Hence, attribute is not generated here and should not be disposed.
                # therefore: release_self=False
                logging.debug("Com-Release: accessed existing com-object %s" % (com_obj))
                auto_release_com_obj = AutoReleasingComObject(com_obj, release_self=False)
            self._accessed_com_attributes.append(auto_release_com_obj)
            
            return auto_release_com_obj
        else:
            # value is no ComObject
            return com_obj
        
    
    def dispose(self):
        '''
        Releases all ComObjects which were generated during the lifetime of the AutoReleasingComObject-instance.
        
        ComObjects are generated by accessing attributes or methods and are stored internally.
        The attribute/method-access (see __getattr__) wraps these ComObjects in AutoReleasingComObject-instances.
        This allows to store ComObjects which are generated further down the ComObjects-tree.
        
        Dispose will go down this AutoReleasingComObject-tree and call dispose on these instances as well.
        Therefore, all ComObjects accessed in the object-tree are released by a single dispose-call.
        '''
        # release ComObjects generated further down the object-tree
        logging.debug("Com-Release: dispose on %s" % (self))
        for auto_release_com_obj in self._accessed_com_attributes:
            auto_release_com_obj.dispose()
        self._accessed_com_attributes = []
        
        # release wrapped ComObject
        if self._release_self:
            logging.debug("Com-Release: releasing %s" % (self._comobj))
            Marshal.ReleaseComObject(self._comobj)
    
    

    

class WrappedDispCallable(object):
    '''
    A WrappedDispCallable instance represents a VBA-DispCallable-object and mimics its logic.
    The representing function can be called by function-call or through array-access.
    If the returned object is a ComObject, the object is wrapped as AutoReleasingComObject.
    '''
    
    def __init__(self, auto_release_comobj, method):
        ''' Initialize WrappedDispCallable with an AutoReleasingComObject-instance and an attribute (string). '''
        self._auto_release_comobj = auto_release_comobj
        self._method = method
        
    def __call__(self, *args, **kwargs):
        '''
        Calls the DispCallable-function and returns its result.
        Arguments, which are AutoReleasingComObject-instances are replaced by its ComObject before calling the function.
        If the returned object is a ComObject, the object is wrapped as AutoReleasingComObject.
        '''
        args_converted   = [x._comobj if isinstance(x, AutoReleasingComObject) else x for x in args]
        kwargs_converted = {key: value._comobj if isinstance(value, AutoReleasingComObject) else value for key,value in kwargs.items()}
        # call ComObject's method
        return_value = getattr(self._auto_release_comobj._comobj, self._method)(*args_converted, **kwargs_converted)
        # return wrapped ComObject
        return self._auto_release_comobj.create_and_register_auto_release_com_object(return_value)
    
    def __getitem__(self, key):
        '''
        Allow array-access to the DispCallable-function, so that all of the following
        calls work and return the same result
          foo.item(1), foo.item[1]
          foo.item(1,2), foo.item[1,2]
        '''
        if type(key) == tuple:
            # convert tuple to argument list
            return self.__call__(*key)
        else:
            return self.__call__(key)
    
    


class AutoReleasingComIterator(object):
    def __init__(self, comobj, autorelease_callback):
        self._comobj = comobj
        self._autorelease_callback = autorelease_callback
        self._index = 0
        
    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        if self._index > self._comobj.Count:
            raise StopIteration
        item = self.Item(self._index)
        return self._autorelease_callback(item)
        
        

