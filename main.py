

###### OPERACJE NA SCIEZKACH
#############################
#############################

def parts(path): 
    components = []  
    while True: 
        (path,tail) = os.path.split(path) 
        if tail == "": 
            components.reverse() 
            return components 
        components.append(tail) 

def url_fix(s, charset='utf-8'): 
    if isinstance(s, unicode): 
        s = s.encode(charset, 'ignore') 
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s) 
    path = urllib.quote(path, '/%') 
    qs = urllib.quote_plus(qs, ':&=') 
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor)) 

def rewritepath(os,path): 

    components = parts(path) 
    newpath = ""

    if os == 'nt':
       for item in components:
           newpath = newpath + "\\" + item

    elif os == 'posix':
         for item in components:
             newpath = newpath + "/" + item

    elif os == 'url':
         for item in components:
             newpath = newpath + "/" + item
         newpath = url_fix(newpath)

    newpath = newpath[1:]
    return newpath

def putin(string,filename,method):
	if method == "append":
		putinfile = open(filename,"a")
	else:
		putinfile = open(filename,"w")
	putinfile.write(string)
	putinfile.close
	
def orphilia_notify(method,string):
	f = open(os.path.normpath(configurationdir + '/notify-settings'), 'r')
	notifier = f.read()
	f.close
	os.system(notifier + ' ' + method + ' \"'+ string + '\"')

###### DELTA UJEMNA I INNE TRAGEDIE
############################
############################

# We track the folder state as a tree of Node objects.

class Node(object):
    def __init__(self, path, content):
        # The "original" path (i.e. not the lower-case path)
        self.path = path
        # For files, content is a pair (size, modified)
        # For folders, content is a dict of children Nodes, keyed by lower-case file names.
        self.content = content
    def is_folder(self):
        return isinstance(self.content, dict)
    def to_json(self):
        return (self.path, Node.to_json_content(self.content))
    @staticmethod
    def from_json(jnode):
        path, jcontent = jnode
        return Node(path, Node.from_json_content(jcontent))
    @staticmethod
    def to_json_content(content):
        if isinstance(content, dict):
            return dict([(name_lc, node.to_json()) for name_lc, node in content.iteritems()])
        else:
            return content
    @staticmethod
    def from_json_content(jcontent):
        if isinstance(jcontent, dict):
            return dict([(name_lc, Node.from_json(jnode)) for name_lc, jnode in jcontent.iteritems()])
        else:
            return jcontent

def apply_delta(root, e):
    path, metadata = e
    branch, leaf = split_path(path)

    if metadata is not None:
        sys.stdout.write('+ %s\n' % path)
        # Traverse down the tree until we find the parent folder of the entry
        # we want to add.  Create any missing folders along the way.
        children = root
        for part in branch:
            node = get_or_create_child(children, part)
            # If there's no folder here, make an empty one.
            if not node.is_folder():
                node.content = {}
            children = node.content

        # Create the file/folder.
        node = get_or_create_child(children, leaf)
        node.path = metadata['path']  # Save the un-lower-cased path.
        if metadata['is_dir']:
            # Only create an empty folder if there isn't one there already.
            if not node.is_folder():
                node.content = {}
        else:
            node.content = metadata['size'], metadata['modified']
    else:
        sys.stdout.write('- %s\n' % path)
        # Traverse down the tree until we find the parent of the entry we
        # want to delete.
        children = root
        for part in branch:
            node = children.get(part)
            # If one of the parent folders is missing, then we're done.
            if node is None or not node.is_folder(): break
            children = node.content
        else:
            # If we made it all the way, delete the file/folder (if it exists).
            if leaf in children:
                del children[leaf]

def get_or_create_child(children, name):
    child = children.get(name)
    if child is None:
        children[name] = child = Node(None, None)
    return child

def split_path(path):
    assert path[0] == '/', path
    assert path != '/', path
    parts = path[1:].split('/')
    return parts[0:-1], parts[-1]

# Recursively search 'tree' for files that contain the string in 'term'.
# Print out any matches.
def search_tree(results, tree, term):
    for name_lc, node in tree.iteritems():
        path = node.path
        if (path is not None) and term in path:
            if node.is_folder():
                results.append('%s' % (path,))
            else:
                size, modified = node.content
                results.append('%s  (%s, %s)' % (path, size, modified))
        # Recurse on children.
        if node.is_folder():
            search_tree(results, node.content, term)

def load_state():
    if not os.path.exists(STATE_FILE):
        sys.stderr.write("ERROR: Couldn't find state file %r.  Run the \"link\" subcommand first.\n" % (STATE_FILE))
        sys.exit(1)
    f = open(STATE_FILE, 'r')
    state = json.load(f)
    state['tree'] = Node.from_json_content(state['tree'])
    f.close()
    return state

def save_state(state):
    f = open(STATE_FILE, 'w')
    state['tree'] = Node.to_json_content(state['tree'])
    json.dump(state, f, indent=4)
    f.close()


###### MANIPULACJE NA DATACH
############################
############################			

def month_int(month):	
	if month == "Jan":
	   month = "01"
	elif month == "Feb":
	   month = "02"
	elif month == "Mar":
	   month = "03"
	elif month == "Apr":
	   month = "04"
	elif month == "May":
	   month = "05"
	elif month == "Jun":
	   month = "06"
	elif month == "Jul":
	   month = "07"
	elif month == "Aug":
	   month = "08"
	elif month == "Sep":
	   month = "09"
	elif month == "Oct":
	   month = "10"
	elif month == "Nov":
	   month = "11"
	elif month == "Dec":
	   month = "12"
	return month
	
def translate_date(date1):
	day = date1[:2]
	date1 = date1[3:]
	month = month_int(date1[:3])
	date1 = date1[4:]
	year = date1[:4]
	date1 = date1[5:]
	hour = date1[:2]
	date1 = date1[3:]
	minute = date1[:2]
	date1 = date1[3:]
	second = date1[:2]

	hour = str(int(hour) +1)
	return year + month + day + hour + minute + "." + second

def generate_timestampd(date):
	day = date[:2]
	date = date[3:]
	month = month_int(date[:3])
	date = date[4:]
	year = date[:4]
	date = date[5:]
	hour = date[:2]
	date = date[3:]
	minute = date[:2]
	date = date[3:]
	second = date[:2]

	hour = str(int(hour) +1)

	return (((((int(year) * 12) + int(month)) * 30 + int(day)) * 24 + int(hour)) * 60 + int(minute)) * 60

def generate_modifytime(date):
	day = date[:2]
	date = date[3:]
	month = date[:3]
	date = date[4:]
	year = date[:4]
	date = date[5:]
	hour = date[:2]
	date = date[3:]
	minute = date[:2]
	date = date[3:]
	second = date[:2]

	modifytime = day + " " + month + " " + year + " " + hour + ":" + minute
	return modifytime
	
def generate_timestamp(date):
	print date
	month = month_int(date[:3])
	print month
	date = date[4:]
	print date
	day = date[:2]
	print day
	date = date[3:]
	print date
	hour = date[:2]
	print hour
	date = date[3:]
	print date
	minute = date[:2]
	print minute
	date = date[3:]
	print date
	second = date[:2]
	print second
	date = date[3:]
	print date
	year = date
	print year

	return (((((int(year) * 12) + int(month)) * 30 + int(day)) * 24 + int(hour)) * 60 + int(minute)) * 60


#####################################################
###################################################
######################## TU ZACZYNA SIE KLIENT!

if wtd == "--client":
    reload(sys).setdefaultencoding('utf8')
    print "Orphilia"
    print "[Maciej Janiszewski, 2010-2012]"
    print "based on Dropbox SDK from https://www.dropbox.com/developers/reference/sdk"
    print ""
    wtd = "--client--silent"

def login_and_authorize(authorize_url):   
    br = mechanize.Browser()
    br.open('https://www.dropbox.com/login')
    isLoginForm = lambda l: l.action == "https://www.dropbox.com/login" and l.method == "POST"
    try:
      br.select_form(predicate=isLoginForm)
    except:
      print(" [!] Unable to find login form.");
      exit(1);
    br['login_email'] = email
    br['login_password'] = password
    response = br.submit()
    br.open(authorize_url)
    print " OK"
    return

if wtd == "--client--silent":
	statusf = open(os.path.normpath(configurationdir+'/net-status'), 'r')
	status = statusf.read()
	statusf.close()
	if status == "1":
		exit()
	read_details = open(os.path.normpath(configurationdir+'/dropbox-path'), 'r')
	droppath = read_details.read()
	read_details.close()

	def command(login_required=True):
	    def decorate(f):
	        def wrapper(self, args):
	            if login_required and not self.sess.is_linked():
	                self.stdout.write("Please 'login' to execute this command\n")
	                return
	
	            try:
	                return f(self, *args)
	            except TypeError, e:
	                self.stdout.write(str(e) + '\n')
	            except ErrorResponse, e:
	               msg = e.user_error_msg or str(e)
	               self.stdout.write('Error: %s\n' % msg)
	               msg2 = msg[:5]
	               if msg2 == "[401]":
		               print(" > Token problem. Unlinking..."),
		               self.sess.unlink()
		               print(" OK")
		               self.sess.link()
		               print(" > Repeating command...")
		               term = DropboxTerm(APP_KEY, APP_SECRET)
		               term.onecmd(sys.argv[2])
	
	        wrapper.__doc__ = f.__doc__
	        return wrapper
	    return decorate

	class DropboxTerm(cmd.Cmd):
	    def __init__(self, app_key, app_secret):
	        cmd.Cmd.__init__(self)
	        self.sess = StoredSession(app_key, app_secret, access_type=ACCESS_TYPE)
	        self.api_client = DropboxClient(self.sess)
	
	        self.sess.load_creds()

	    @command()
	    def do_delta(self):
	        state = load_state()
	        cursor = state.get('cursor')
	        tree = state['tree']
	        page = 0
	        changed = False
	        page_limit = 5
	        while (page_limit is None) or (page < page_limit):
	           # Get /delta results from Dropbox
	           result = self.api_client.delta(cursor)
	           page += 1
	           if result['reset'] == True:
	              sys.stdout.write('reset\n')
	              changed = True
	              tree = {}
	           cursor = result['cursor']
	           # Apply the entries one by one to our cached tree.
	           for delta_entry in result['entries']:
	                changed = True
	                apply_delta(tree, delta_entry)
	                cursor = result['cursor']
	                if not result['has_more']: break

	        if not changed:
	            sys.stdout.write('No updates.\n')
	        else:
	        # Save state
	           state['cursor'] = cursor
	           state['tree'] = tree
	           save_state(state)
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_ls(self,path, to_file):
	        resp = self.api_client.metadata(path)
	        file = open(to_file,"w")

	        if 'contents' in resp:
	            for f in resp['contents']:
	                name = os.path.basename(f['path'])
	                encoding = locale.getdefaultlocale()[1]
	                file.write(('%s\n' % name).encode(encoding))
	        file.close()
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_ls_alt(self, path, to_file):
	        resp = self.api_client.metadata(path)
		a = unicode(resp)
	        file = open(to_file,"w")
		print >> file, a
	        file.close()
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_sync_everything(self, path):
	        term = DropboxTerm(APP_KEY, APP_SECRET)
	        resp = self.api_client.metadata(path)
	        rand1 = random.random()
	        dirlist = os.listdir(droppath + "/" + path)
	        to_file = os.path.normpath(configurationdir + "_tmpscript" + str(rand1) + ".tmp")
	        file = open(to_file,"w")
	        file.write('orphilia --client--silent \"sync_folder \\"' + path + "/" + '\\"\"' + '\n')

	        for fname in dirlist:
	                if os.path.isdir(droppath + "/" + path + fname):
			        file.write('cd \"' + fname + '\"'+ '\n')
			        file.write('orphilia --client--silent \"sync_everything \\"' + path + "/" + fname + '\\"\"' + '\n')
			        file.write('cd ..'+ '\n')
	        file.close()
	        os.system("chmod +x " + to_file)
	        os.system("sh " + to_file)
	        os.system("rm " + to_file)
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_get(self, path, to_path):
	        resp = self.api_client.metadata(path)
	        modified = resp['modified']
	        date1 = modified[5:]
	        date1 = generate_modifytime(date1)
	        f = self.api_client.get_file("/" + path)
	        file = open(to_path,"w")
		file.write(f.read())
	        file.close()
	        os.system("touch -d \"" + date1 + "\" \"" + to_path + "\"")
	        
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_sync_folder(self, path):
		term = DropboxTerm(APP_KEY, APP_SECRET)
	        """"""
	        resp = self.api_client.metadata(path)
	        dirlist = os.listdir(droppath + "/" + path)
	        rand1 = random.random()

	        if 'contents' in resp:
	            for f in resp['contents']:
		        name = os.path.basename(f['path'])
		        encoding = locale.getdefaultlocale()[1]
	                if ('%s' % name).encode(encoding) not in dirlist:
	                        print ('%s' % name).encode(encoding) + " not found."
		                if not os.path.isfile(('%s' % name).encode(encoding)):
				        dir = f['is_dir']
				        if not dir:
				                term.onecmd('get \"' + path + "/" + ('%s' % name).encode(encoding) + '\" \"' +  droppath + "/" + path +  ('%s' % name).encode(encoding) + '\"')
				        if dir:
				                os.system('mkdir \"' + droppath + "/" + path +  ('%s' % name).encode(encoding) + '\"')
	                else:
		                name = os.path.basename(f['path'])
		                encoding = locale.getdefaultlocale()[1]
	                        print ('%s' % name).encode(encoding) + " found. Checking..."

		                modified = f['modified']
		                date1 = modified[5:]
		                if os.path.isfile(('%s' % name).encode(encoding)):
				        t = time.ctime(os.path.getmtime(('%s' % name).encode(encoding)))
				        date2 = t[4:]

				        hour = str(int(hour) +1)

				        timestamp1_rnd = generate_timestampd(date1)
				        print(date1 + " converted to " + timestamp1_rnd)
				        timestamp2_rnd = generate_timestamp(date2)
				        print(date2 + " converted to " + timestamp2_rnd)
				        
			                dir = f['is_dir']

					if timestamp1_rnd < timestamp2_rnd:
				                if not dir:

						        print " - Dropbox verion of file \"" + ('%s' % name).encode(encoding) + "\" is older. Updating..."
						        term.onecmd('rm \"' +  path + "/" + ('%s' % name).encode(encoding) + '\"')
						        term.onecmd('sync \"' + ('%s' % name).encode(encoding) + '\" \"' +  path + "/" + ('%s' % name).encode(encoding) + '\"')
				                else:
						        print + " x " + name + " is directory. Skipping."

					elif timestamp1_rnd > timestamp2_rnd:
						  term.onecmd('get \"' + path + "/" + ('%s' % name).encode(encoding) + '\" \"' +  ('%s' % name).encode(encoding) + '\"')
					          print " - Dropbox verion of file \"" + ('%s' % name).encode(encoding) + "\" is newer. Updating."

					else:
					        print " x File \"" + ('%s' % name).encode(encoding) + "\" is identical. Skipping."
								      

		        print " > Command '" + sys.argv[2] + "' executed"
	
	    @command()
	    def do_logout(self):
	        self.sess.unlink()
	        print " > Unlinked ;("

	    @command()
	    def do_cat(self, path):
	        f = self.api_client.get_file("/" + path)
	        self.stdout.write(f.read())
	        self.stdout.write("\n")

	    @command()
	    def do_mkdir(self, path):
	        self.api_client.file_create_folder("/" + path)
	        print " > Directory \'" + path + "\' created"
	
	    @command()
	    def do_rm(self, path):
	        """delete a file or directory"""
	        self.api_client.file_delete("/" + path)
	        orphilia_notify('rm',path)

	    @command()
	    def do_mv(self, from_path, to_path):
	        """move/rename a file or directory"""
	        self.api_client.file_move("/" + from_path,
	                                  "/" + to_path)
	        print " > Command '" + sys.argv[2] + "' executed"
	
	    @command()
	    def do_account_info(self):
	        f = self.api_client.account_info()
	        pprint.PrettyPrinter(indent=2).pprint(f)
	        print " > Command '" + sys.argv[2] + "' executed"

	    @command()
	    def do_uid(self, parameter2):
	        f = self.api_client.account_info()
	        uid = str(f['uid'])
	        putin(uid,parameter2,'rewrite')
	        print " > UID updated"

	    @command()
	    def do_put(self, from_path, to_path):
	        from_file = open(os.path.expanduser(from_path))

	        self.api_client.put_file("/" + to_path, from_file)
	        orphilia_notify('add',from_path)

	    @command()
	    def do_upd(self, from_path, to_path):
	        from_file = open(os.path.expanduser(from_path))
	        
	        self.api_client.rm_file("/" + to_path)
	        self.api_client.put_file("/" + to_path, from_file)
	        orphilia_notify('upd',from_path)
	
	    # the following are for command line magic and aren't Dropbox-related
	    def emptyline(self):
	        pass

	    def do_EOF(self, line):
	        self.stdout.write('\n')
	        return True

	    def parseline(self, line):
	        parts = shlex.split(line)
	        if len(parts) == 0:
	            return None, None, line
	        else:
	            return parts[0], parts[1:], line


	class StoredSession(DropboxSession):
	    TOKEN_FILE = os.path.normpath(configurationdir + "/token_store.txt")

	    def load_creds(self):
	        print " > Loading access token...",
	        try:
	            stored_creds = open(self.TOKEN_FILE).read()
	            self.set_token(*stored_creds.split('|'))
	            print " OK"
	        except IOError:
	            print " FAILED"
	            print " x Access token not found. Beggining new session."
	            self.link()

	    def write_creds(self, token):
	        f = open(self.TOKEN_FILE, 'w')
	        f.write("|".join([token.key, token.secret]))
	        f.close()

	    def delete_creds(self):
	        os.unlink(self.TOKEN_FILE)
	
	    def link(self):
	        print " > Authorizing..."
	        request_token = self.obtain_request_token()
	        url = self.build_authorize_url(request_token)
	        if sys.platform[:5] == "haiku":
	              putin(url,os.path.normpath(configurationdir+'/authorize-url'),'rewrite')
	              drmchujnia = os.system("orphilia_haiku-authorize")
	              ###os.system('rm ' + os.path.normpath(configurationdir+'/authorize-url'))
	        else:
	              print "url:", url,
	              raw_input()

	        self.obtain_access_token(request_token)
	        self.write_creds(self.token)

	        save_state({
	            'access_token': (request_token.key, request_token.secret),
	            'tree': {}
	        })

	    def unlink(self):
	        self.delete_creds()
	        DropboxSession.unlink(self)


	def main():
	    if APP_KEY == '' or APP_SECRET == '':
	        exit("You need to set your APP_KEY and APP_SECRET!")
	    term = DropboxTerm(APP_KEY, APP_SECRET)
	    term.onecmd(sys.argv[2])
	
	if __name__ == '__main__':
	    main()


########################### ALTERNATYWNE KOMENDY
################################################

elif wtd == "--install":
       print "Orphilia Installer"
       print "---"
       if sys.platform[:5] == "haiku":
         print "Copying files..."
         os.system("chmod +x ./orphilia")
         os.system("mkdir /boot/apps/orphilia")
         os.system("cp orphilia /boot/apps/orphilia")
         os.system("cp notify/haiku-notify /boot/apps/orphilia/haiku-notify")
         os.system("cp branding/orphilia_haiku.png /boot/apps/orphilia")
         os.system("cp authorize.yab /boot/apps/orphilia/authorize")
         os.system("cp yab /boot/apps/orphilia")
         os.system("cp trusted-certs.crt /boot/apps/orphilia")
         os.system("ln -s /boot/apps/orphilia/orphilia /boot/common/bin/orphilia")
         os.system("ln -s /boot/apps/orphilia/haiku-notify /boot/common/bin/orphilia_haiku-notify")
         os.system("ln -s /boot/apps/orphilia/authorize /boot/common/bin/orphilia_haiku-authorize")
         os.system('alert --info \"Installation completed.\"')
       else:
          print "Copying files..."
          os.system("chmod +x ./orphilia")
          os.system("cp orphilia /usr/bin")
          os.system("cp notify/cli-notify /usr/bin/orphilia_cli-notify")
          os.system("cp notify/notifysend-notify /usr/bin/orphilia_notifysend-notify")
          os.system("cp trusted-certs.crt /usr/bin")
          os.system("cp ./branding/orphilia.png /usr/share/pixmaps")

       print "Done. Now run orphilia --configuration as regular user"

elif wtd == "--uninstall":
       print "Orphilia Installer"
       print "---"
       if sys.platform[:5] == "haiku":
          print "Removing files..."
          os.system("rm -r /boot/apps/orphilia")
          os.system("rm /boot/common/bin/orphilia")
          os.system("rm /boot/common/bin/orphilia_haiku-notify")
          os.system("rm /boot/common/bin/orphilia_haiku-authorize")
          os.system('alert --info \"Uninstallation completed.\"')
       else:
          print "Removing files..."
          os.system("rm /usr/bin/orphilia")
          os.system("rm /usr/bin/orphilia_cli-notify")
          os.system("rm /usr/bin/orphilia_notifysend-notify")
          os.system("rm /usr/bin/trusted-certs.crt")
          os.system("rm /usr/share/pixmaps/orphilia.png")
       print "Done."

################################################
################################################

elif wtd == "--help":
	print("\n")
	print("Syntax: orphilia [OPTION] [PARAMETERS]")
	print("")
	print("  --help          - displays this text")
	print("  --monitor       - monitors Dropbox folder activity")
	print("  --configuration - runs configuration wizard")
	print("  --public        - generates public links")
	print("  --install       - installs Orphilia")
	print("  --uninstall     - uninstalls Orphilia")
	print("  --client        - runs Orphilia API Client")
	print('     syntax: orphilia --client "\\"[parameter1]\\" \\"[parameter2]\\" \\"[parameter3]\\""')
	print("       get    - downloads file from path specified in parameter2 and saves them to \npath specified in parameter3")
	print("       put    - uploads file from path specified in parameter2 to path specified in \nparameter3")
	print("       mv     - moves file from path specified in parameter2 to path specified in \nparameter3")
	print("       cp     - copies file from path specified in parameter2 to path specified in \nparameter3")
	print("       rm     - removes a file (name specified in parameter2)")
	print("       ls     - creates a list of files in directory specified in parameter2 and \nsaves it to file specified in parameter3")
	print("       mkdir  - creates a directory (name specified in parameter2)")
	print("       uid    - updates Orphilia configuration with current accounts Dropbox UID")

elif wtd == "--configuration":
	if os.path.isdir(configurationdir):
		shutil.rmtree(configurationdir)
	os.makedirs(configurationdir)
	putin('0',os.path.normpath(configurationdir+'/net-status'),'rewrite')
	print("Welcome to Orphilia, an open-source crossplatform Dropbox client.\nIn few steps, you will configure your Dropbox account to be used with Orphilia.")
	
	if sys.platform[:5] == "haiku":
		putin('orphilia_haiku-notify',os.path.normpath(configurationdir+'/notify-settings'),'rewrite')

	else:
		notifier = raw_input("Enter notify method: ")
		putin(notifier,os.path.normpath(configurationdir+'/notify-settings'),'rewrite')

	droppath = raw_input("Dropbox folder location (optional):")
	
	if droppath == "":	
		droppath = os.path.normpath(home + '/Dropbox')
	else:
		pass
		
	putin(droppath,os.path.normpath(configurationdir+'/dropbox-path'),'rewrite')
	if not os.path.exists(droppath):
 		os.makedirs(droppath)

	print("Please wait. Orphilia is making configuration files.")
	os.system('orphilia --client--silent \"uid \''+os.path.normpath(configurationdir+'/dropbox-id') + '\'\"')

	print("Configuration files has been created.")

elif wtd == "--configuration-haiku":
	if os.path.isdir(configurationdir):
		shutil.rmtree(configurationdir)
	os.makedirs(configurationdir)
	putin('0',os.path.normpath(configurationdir+'/net-status'),'rewrite')
	
	putin('orphilia_haiku-notify',os.path.normpath(configurationdir+'/notify-settings'),'rewrite')

	droppath = sys.argv[2]
	
	if droppath == "default":	
		droppath = os.path.normpath(home + '/Dropbox')
	else:
		pass
		
	putin(droppath,os.path.normpath(configurationdir+'/dropbox-path'),'rewrite')
	if not os.path.exists(droppath):
 		os.makedirs(droppath)

	os.system('orphilia --client--silent \"uid \''+os.path.normpath(configurationdir+'/dropbox-id') + '\'\"')

elif wtd == "--public":
	read_details = open(os.path.normpath(configurationdir+'/dropbox-path'), 'r')
	DROPPATH = read_details.read()
	read_details.close()
	read_details2 = open(os.path.normpath(configurationdir+'/dropbox-id'), 'r')
	DROPID = read_details2.read()
	read_details2.close()
	par = sys.argv[2]
	link = 'http://dl.dropbox.com/u/' + DROPID + '/' + rewritepath('url',par[len(os.path.normpath(DROPPATH + "/Public"))+1:])
	orphilia_notify('link',link)

elif wtd == "--monitor":
    class LoggingEventHandler(FileSystemEventHandler):
        """Logs all the events captured."""

        def on_moved(self, event):
            super(LoggingEventHandler, self).on_moved(event)
            par = event.src_path
            path = par[len(droppath)+1:]
            par2 = event.dest_path
            path2 = par2[len(droppath)+1:]

            what = 'directory' if event.is_directory else 'file'
            if what == "file":
                 os.system('orphilia --client--silent \"mv \\"' + path + '\\" \\"' + path2 + '\\"\"')
            else:
                 os.system('orphilia --client--silent \"mkdir \'' + path2 + '\'\"')
                 os.system('orphilia --client--silent \"rm \'' + path + '\'\"')
            logging.info("Moved %s: from %s to %s", what, event.src_path,
                         event.dest_path)

        def on_created(self, event):
            super(LoggingEventHandler, self).on_created(event)
            if os.name <> "nt":
                    what = 'directory' if event.is_directory else 'file'
                    if what == 'file':
                            par = event.src_path
                            while True:
                                  size1 = os.path.getsize(par)
                                  time.sleep(0.5)
                                  size2 = os.path.getsize(par)
                                  if size1 == size2:
                                     break
                            path = par[len(droppath)+1:]
                            os.system('orphilia --client--silent \"put \\"' + droppath +"/"+ path + '\\" \\"' + path + '\\"\"')
                    else:
                            par = event.src_path
                            path = par[len(droppath)+1:]
                            print('orphilia --client--silent \"mkdir \'' + path + '\'\"')
                            os.system('orphilia --client--silent \"mkdir \'' + path + '\'\"')
                    logging.info("Created %s: %s", what, event.src_path)
            else:
                    what = 'directory' if event.is_directory else 'file'
                    if what == 'directory':
                            par = event.src_path
                            path = par[len(droppath)+1:]
                            os.system('orphilia --client--silent \"mkdir \'' + path + '\'\"')
                            logging.info("Created %s: %s", what, event.src_path)

        def on_deleted(self, event):
            super(LoggingEventHandler, self).on_deleted(event)
            par = event.src_path
            path = par[len(droppath)+1:]
            what = 'directory' if event.is_directory else 'file'
            os.system('orphilia --client--silent \"rm \'' + path + '\'\"')
            logging.info("Deleted %s: %s", what, event.src_path)

        def on_modified(self, event):
            super(LoggingEventHandler, self).on_modified(event)

            what = 'directory' if event.is_directory else 'file'
            if what == "file":
               par = event.src_path
               path = par[len(droppath)+1:]
               if os.name <> "nt":
                  os.system('orphilia --client--silent \"rm \'' + path + '\'\"')
               os.system('orphilia --client--silent \"upd \'' + droppath +"/"+ path + '\' \'' + path + '\'\"')
            logging.info("Modified %s: %s", what, event.src_path)

    if __name__ == "__main__":
      read_details = open(os.path.normpath(configurationdir+'/dropbox-path'), 'r')
      droppath = read_details.read()
      read_details.close()

      logging.basicConfig(level=logging.INFO,
                          format='%(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
      event_handler = LoggingEventHandler()
      observer = Observer()
      observer.schedule(event_handler, droppath, recursive=True)
      observer.start()
      try:
        while True:
          time.sleep(1)
          statusf = open(os.path.normpath(configurationdir+'/net-status'), 'r')
          status = statusf.read()
          statusf.close()
          if status == "1":
             exit()
      except KeyboardInterrupt:
        observer.stop()
        observer.join()

else:
     print("Invalid syntax. Type orphilia --help for more informations")
