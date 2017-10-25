package pegaagentstatus;
import javax.management.MBeanServerConnection;
import javax.management.ObjectName;
import javax.management.remote.JMXConnector;
import javax.management.remote.JMXConnectorFactory;
import javax.management.remote.JMXServiceURL;
import javax.naming.Context;
import java.io.IOException;
import java.util.Arrays;
import java.util.Hashtable;

public class PegaAgentStatus {

    private JMXConnector readConnector = null;
 
    public static void main(String[] args) {
        
        if(args.length != 5){
            System.out.println("You must use only 5 argument instead " +  args.length);
            System.out.println("Example: PegaAgentStatus.jar localhost:7001 server2 username password");
            System.exit(0);
        }
        
        String hostname_port = args[0];
        String location = args[1];
        String id = args[2];
        String username = args[3];
        String password = args[4];
        
        PegaAgentStatus pega_agent_status = new PegaAgentStatus();
        Object agent_status = pega_agent_status.GetClusterInfo(hostname_port, location, id, username, password);
        System.out.println(agent_status);
        pega_agent_status.closeConnectors();
                
    }
 
    private Object GetClusterInfo(String hostname_port, String location, String id, String username, String password) {        
        final String weblogicReadMbeanServer = "weblogic.management.mbeanservers.domainruntime";
        final String readUrl = "service:jmx:t3://" + hostname_port + "/jndi/" + weblogicReadMbeanServer;
        final String pointToPoint = "com.pega.PegaRULES:Location=" + location + ",name=com.pega.pegarules.management.internal.AgentManagement,type=enterprise,id=\"" + id + "\"";
 
        try {
            readConnector = getMBeanConnector(readUrl, username, password);
            MBeanServerConnection readConnection = readConnector.getMBeanServerConnection();    
            ObjectName coherencePointToPointObjectName = new ObjectName(pointToPoint);            
            Object ret = readConnection.invoke(coherencePointToPointObjectName, "AgentStatus", null, null);
            return ret;
 
        } catch (Exception e) {
            e.printStackTrace();
            closeConnectors();
        }
        return null;        
    }
 
    private JMXConnector getMBeanConnector(String urlPath, String username, String password) throws IOException {
        JMXServiceURL serviceURL = new JMXServiceURL(urlPath);
        Hashtable<String, String> hashtable = new Hashtable<String, String>();
        hashtable.put(Context.SECURITY_PRINCIPAL, username);
        hashtable.put(Context.SECURITY_CREDENTIALS, password);
        hashtable.put(JMXConnectorFactory.PROTOCOL_PROVIDER_PACKAGES, "weblogic.management.remote");
 
        return JMXConnectorFactory.connect(serviceURL, hashtable);
    }
 
    private void closeConnectors() {
        try {
            if (readConnector != null) {
                readConnector.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
}
