package us.pfrommer.insteon.utils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;

public interface ResourceLocator {
	public InputStream getResource(String resource);
	
	public class ClasspathResourceLocator implements ResourceLocator {
		public InputStream getResource(String resource) {
			InputStream in = ResourceLocator.class.getClassLoader().getResourceAsStream(resource);
			if (in == null) throw new RuntimeException("Resource " + resource + " not found");
			return in;
		}
	}
	public class FolderResourceLocator implements ResourceLocator {
		private File m_file;
		public FolderResourceLocator(File file) {
			m_file = file;
		}
		public InputStream getResource(String resource) {
			try {
				return new FileInputStream(new File(m_file, resource));
			} catch (FileNotFoundException e) {
				throw new RuntimeException(e);
			}
		}
	}
}
