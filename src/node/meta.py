from zope.interface import implements
from node.interfaces import (
    INode,
    IBehavior,
)

def before():
    """Behavior before hook decorator.
    """

def after():
    """Behavior before hook decorator.
    """

class behavior(object):
    """Decorator for extending nodes by behaviors.
    """
    
    def __init__(self, *behaviors):
        for beh in behaviors:
            if not IBehavior.implementedBy(beh):
                msg = '``IBehavior`` not implemented by ``%s``' % beh.__name__
                raise TypeError(msg)
        self.behaviors = behaviors

    def __call__(self, obj):
        if not INode.implementedBy(obj):
            msg = '``INode`` not implemented by ``%s``' % obj.__name__
            raise TypeError(msg)
        
        ###
        # node wrapper metaclass.
        
        class NodeBehaviorMeta(type):
            """Metaclass for NodeBehaviorWrapper.
            
            Writes behavior class objects to cls.__behaviors_cls and creates
            empty dict cls.__behaviors_ins, which later contains the bahavior
            class instances.
            """
            
            def __init__(cls, name, bases, dct):
                setattr(cls, '__behaviors_cls', self.behaviors)
                super(NodeBehaviorMeta, cls).__init__(name, bases, dct)
        
        ###
        # wrapper for decorated node.
        
        class NodeBehaviorWrapper(obj):
            """Derives from given ``obj`` by decorator and wrap node behavior.
            """
            __metaclass__ = NodeBehaviorMeta
            __default_marker = object()
            
            implements(INode) # after __metaclass__ definition.
            
            def __getattribute__(self, name):
                # ``super`` is at such places confusing and seem to be buggy as
                # well. address directly where we want to do something.
                try:
                    # try to return requested attribute from self (the node)
                    return obj.__getattribute__(self, name)
                except AttributeError, e:
                    # try to find requested attribute on behavior
                    # create behavior instance if necessary
                    behaviors = obj.__getattribute__(self, '__behaviors_cls')
                    try:
                        ins = obj.__getattribute__(self, '__behaviors_ins')
                    except AttributeError:
                        obj.__setattr__(self, '__behaviors_ins', dict())
                        ins = obj.__getattribute__(self, '__behaviors_ins')
                    for behavior in behaviors:
                        unbound = getattr(behavior, name, self.__default_marker)
                        if unbound is self.__default_marker:
                            continue
                        b_name = behavior.__name__
                        instance = ins.get(b_name, self.__default_marker)
                        if instance is self.__default_marker:
                            instance = ins[b_name] = behavior(self)
                        return getattr(instance, name)
                    raise AttributeError(name)
            
            def __repr__(self):
                name = unicode(self.__name__).encode('ascii', 'replace')
                return "<%s object '%s' at %s>" % (obj.__name__,
                                                   name,
                                                   hex(id(self))[:-1])
            
            __str__ = __repr__
            
            @property
            def noderepr(self):
                return "<%s object of '%s' at %s>" % (self.__class__.__name__,
                                                      obj.__name__,
                                                      hex(id(self))[:-1])
        
        # return wrapped
        return NodeBehaviorWrapper
