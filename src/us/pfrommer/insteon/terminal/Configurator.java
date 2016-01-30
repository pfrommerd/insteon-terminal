package us.pfrommer.insteon.terminal;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.utils.ResourceLocator;

// Responsible for managing insteon-terminal files
public class Configurator {
	private static final Logger logger = LoggerFactory.getLogger(Configurator.class);

	private String[] m_pythonPath = null;
	
	public Configurator() {

	}

	public void loadConfig(ResourceLocator locator) {
		InputStream config = locator.getResource("insteon-terminal.conf");

		logger.trace("Loading config");
		
		if (config != null) {
			Properties prop = new Properties();
			try {
				prop.load(config);
				String mode = prop.getProperty("mode");
				
				String prefix = mode + "/";
				if (mode.isEmpty()) prefix = "";
								
				String path = prop.getProperty(prefix + "python_path");

				if (path != null) m_pythonPath = path.split(":");

			
				logger.trace("Config loaded!");			
			
			} catch (IOException e) {
				logger.error("Could not load config", e);
			}
		} else {
			logger.error("Could not find 'insteon-terminal.conf'!");
		}
	}
	
	public void configure(InsteonTerminal t) {
		if (m_pythonPath != null) {
			for (String p : m_pythonPath) {
				p = p.replaceFirst("^~", System.getProperty("user.home")); // Handle ~
				
				t.addModuleSearchPath(p);
			}
		}
	}
	
}
