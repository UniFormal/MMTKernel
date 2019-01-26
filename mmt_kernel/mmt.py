# Python side of Java-Python bridge
# see info.kwarc.mmt.python.Py4JGateway (an MMT extension that must be added to MMT for the bridge to work) for the counterpart

from py4j.java_gateway import JavaGateway, JavaObject, GatewayParameters, CallbackServerParameters
import py4j

def getJavaGateway(port):
    # create the gateway that communicates with the JVM
    gwp = GatewayParameters(auto_field=True,auto_convert=True,port=port)
    cbp = CallbackServerParameters(port=port+1)
    return JavaGateway(gateway_parameters=gwp,callback_server_parameters=cbp,python_proxy_port=port+1)

def getController(gateway):
    # MMT sets the entry point to be the MMT controller
    return gateway.entry_point

def getMMT(gateway):
    return gateway.jvm.info.kwarc.mmt

def getAPI(mmt):
    # jvm yields access to Java namespace
    return mmt.api

def setupJavaObject(gateway):
    # everything below here are optional improvements to smoothen the Scala-Python integration
    # they also provide examples how to use the bridge


    # General remarks for handling from Python Scala features that are not present in the JVM anymore
    #  companion object: fields are static methods, call as usual
    #  nullary functions: () is mandatory
    #  sequence arguments: needs a Seq, use Seq(pythonlist) conversion
    #  default arguments: all arguments must be provided
    #  implicit conversions: apply explicitly
    #  magic functions: some correspondence established below
    #  symbolic method names as operators: use .M below, some infix operators can be mapped to Python magic functions (see below)

    # make the string representations of JVM objects nicer
    def cut(s,at):
        if len(s) > at-3 or '\n' in s:
            return s.split("\n")[0][:at] + " ..."
        else:
            return s

    JavaObject.__repr__ = lambda self: "<" + self.getClass().getName() + " object (JVM) " + cut(self.toString(), 100) + ">"

    # handle special identifiers: $ is not an idchar in Python
    # use x.M(s) to access method s of x if x has special characters (Python does not allow $ in identifiers)

    dollarReplacements = {"+":"$plus", "-": "$minus", "*": "$star", "/": "$div", "=": "$equals",
                        "!":"$bang", "?":"$qmark", "^":"$up"}
    def dollarReplaceChar(c):
        if c in dollarReplacements:
            return dollarReplacements[c]
        else:
            return c
    def dollarReplace(s):
        return "".join(map(dollarReplaceChar,s))

    JavaObject.M = lambda self,s: py4j.java_gateway.get_method(self,dollarReplace(s))

    # align magic functions (only work if they exist on the Scala side)
    def MagicFun(s):
        return lambda self,*args,**kwargs: self.M(s)(*args,**kwargs)

    JavaObject.__str__  = lambda self: self.toString()
    JavaObject.__call__ = lambda self,*args,**kwargs: self.apply(*args,**kwargs)
    JavaObject.__len__ = lambda self: self.length()
    JavaObject.__contains__ = lambda self,x: self.contains(x)
    JavaObject.__getitem__ = lambda self,x: self.apply(x)
    JavaObject.__setitem__ = lambda self,x,y: self.update(x,y)
    JavaObject.__delitem__ = lambda self,x: self.delete(x)
    JavaObject.__contains__ = lambda self,x: self.contains(x)
    JavaObject.__iter__ = lambda self: self.iterator()
    # needed because we can't inline it in Python
    def iternext(o):
        if o.hasNext():
            return o.next()
        else:
            raise StopIteration
    JavaObject.__next__ = iternext
    JavaObject.__add__ = MagicFun("+") #this would have to be extended for Strings
    JavaObject.__sub__ = MagicFun("-")
    JavaObject.__mul__ = MagicFun("*")
    JavaObject.__mod__ = MagicFun("%")
    JavaObject.__truediv__ = MagicFun("/")
    JavaObject.__lt__ = MagicFun("<")
    JavaObject.__le__ = MagicFun("<=")
    JavaObject.__eq__ = MagicFun("==")
    JavaObject.__ne__ = MagicFun("!=")
    JavaObject.__gt__ = MagicFun(">")
    JavaObject.__ge__ = MagicFun(">=")


def toScalaSeq(gateway,l):
    # convert collections
    jc = gateway.jvm.scala.collection.JavaConverters
    return jc.asScalaBufferConverter(l).asScala().toSeq()
def toScalaList(gateway,l):
    # convert collections
    jc = gateway.jvm.scala.collection.JavaConverters
    return jc.asScalaBufferConverter(l).asScala().toList()
def toScalaMap(gateway,m):
    # convert collections
    jc = gateway.jvm.scala.collection.JavaConverters
    return jc.mapAsScalaMapConverter(m).asScala()
def toScalaLMap(gateway,m):
    # convert collections
    jc = gateway.jvm.scala.collection.JavaConverters
    return jc.mapAsScalaMapConverter(m).asScala().toList()
    