using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace WindowsFormsApplication8
{
    public sealed class SingleConnection
    {
        private static Process pythonEngineProcess;
        private static TcpListener listener;
        private static TcpClient pythonClient;
        private static int PACKET_SIZE = 1024;
        private static readonly SingleConnection instance = new SingleConnection();

        // Explicit static constructor to tell C# compiler
        // not to mark type as beforefieldinit
        static SingleConnection()
        {
        }

        private SingleConnection()
        {
        }

        public static SingleConnection Instance
        {
            get
            {
                return instance;
            }
        }

        public static void Connect()
        {
            // Start listen to the python script socket
            int port = genarate_port();
            IPAddress localAddr = IPAddress.Parse("127.0.0.1");
            listener = new TcpListener(localAddr, port);
            listener.Start();

            // Start to run the script

            run_cmd(port.ToString());
            // wait until the socket from the script will connect
            pythonClient = listener.AcceptTcpClient();
            

            // stop listening because python engine connected to GUI
            listener.Stop();
        }


        // receive and remove @ from the python client
        public static void send(string data)
        {
            pythonClient.Client.Send(Encoding.ASCII.GetBytes(data));
        }
        public static int genarate_port()
        {
            Random rnd = new Random();
            int port = rnd.Next(40000, 50000);
            return port;
        }
        public static void run_cmd(string port)
        {
            try
            {
                project_path path = new project_path();
                System.Diagnostics.Process pythonEngineProcess = new System.Diagnostics.Process();
                pythonEngineProcess.StartInfo.FileName = path.get_interpreter_path();
                pythonEngineProcess.StartInfo.Arguments = path.get_client_file_name() +" " + port;
                pythonEngineProcess.StartInfo.UseShellExecute = false;
                pythonEngineProcess.StartInfo.RedirectStandardOutput = false;
                pythonEngineProcess.Start();
            }
            catch (Win32Exception e)
            {
                EndProcess(e);
            }
            catch (ObjectDisposedException e)
            {
                EndProcess(e);
            }
            catch (InvalidOperationException e)
            {
                EndProcess(e);
            }
            catch (Exception e)
            {
                EndProcess(e);
            }
        }
            

        public static void EndProcess(Exception e)
        {
            if (pythonEngineProcess != null)
            {
                pythonEngineProcess.Dispose();
                pythonEngineProcess = null;
            }
            StopPythonEngine();
        }

        public static void StopPythonEngine()
        {
            try
            {
                if (pythonEngineProcess != null)
                {
                    pythonEngineProcess.Kill();
                    pythonEngineProcess.Dispose();
                    pythonEngineProcess = null;
                }
            }
            catch (Win32Exception e)
            {
                Console.WriteLine(e.Message);
                pythonEngineProcess = null;
            }
            catch (InvalidOperationException e)
            {
                Console.WriteLine(e.Message);
                pythonEngineProcess = null;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                pythonEngineProcess = null;
            }

        }
        // receive and remove @ from the python client
        public static String recv()
        {
            byte[] data = new byte[PACKET_SIZE];
            int numByte = pythonClient.Client.Receive(data);
            string info = Encoding.ASCII.GetString(data,0,numByte);
            return info;
        }
    }

}
