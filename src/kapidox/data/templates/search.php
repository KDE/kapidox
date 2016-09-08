<?php

# Default to ALL in ALL and no class
$version = 'ALL';
if (array_key_exists('version',$_GET)) {
	$version = $_GET['version'];
}

$class = '';
if (array_key_exists('class',$_GET)) {
	$class = $_GET['class'];
}

$module = 'ALL';
if (array_key_exists('module',$_GET)) {
	$module = $_GET['module'];
}

$library = 'ALL';
if (array_key_exists('library',$_GET)) {
	$module = $_GET['library'];
}
$potential_files = false;
$count = 0;

echo empty($class);

if (!empty($class)) {
	$path="searchmaps/map-$version-$module.inc";
	if (file_exists($path)) {
		include $path;
		$loclass = strtolower( $class ); #ensure all the map generators output lower case search terms
		$potential_files = array_keys(preg_grep("/$loclass/", $map));#match *.$loclass.* instead of just $loclass
		$count = count($potential_files);
		if ($count == 0) {
			# Nothing found, return to index via bailout below.
			$file='';
    		} else if ($count == 1) {
			# Single results are redirected immediately
			$file=$potential_files[0];
		} else {
			# TODO: For now, multiple results bails out.
			$file='';
		}
	}
}
if (empty($file)) {
	$file="/index.php?miss=1&class=$class";
}


if ($count <= 1) {
	print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Struct//EN" "DTD/xhtml1-strict.dtd">';
	# Remainder in text block below
?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
        <meta http-equiv="refresh" content="0; url=<?php echo $file;?>"/>
    </head>
</html>
<?php
} else {
	# Multiple results, build page
	$page_title='APIDOX Search Results';
	include 'header.inc';
	echo "<h2>$count results found</h2>";
	echo "<ul>";
	foreach ($potential_files as $file) {
		$file=str_replace("http://api.kde.org/","",$file);
		list($cpart,$mpart,$p,$tmp)=split('/',$file,4);
		$c=str_replace("-api","",$cpart);
		$m=str_replace("-apidocs","",$mpart);
		$bclass=str_replace("_1_1","::",str_replace(".html","",str_replace("class","",basename($file))));
                $project_url="http://api.kde.org/$cpart/$mpart/$p/html/index.html";
		echo "<li><a href=\"$file\">$bclass</a> in module $m-$c, project <a href=\"$project_url\">$p</a></li>\n";
	}
	echo "</ul>";
	include 'footer.inc';
}
?>
