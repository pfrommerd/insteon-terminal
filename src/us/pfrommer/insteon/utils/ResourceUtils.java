package us.pfrommer.insteon.utils;

public class ResourceUtils {
	public static String s_getRelativeResource(String resource, String relativeResource) {
		return s_getParentDirectory(resource) + relativeResource;
	}
	public static String s_getParentDirectory(String resource) {
		return resource.substring(0, resource.lastIndexOf('/') + 1);
	}
}
