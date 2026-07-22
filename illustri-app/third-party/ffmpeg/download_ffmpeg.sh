#!/bin/bash

# Downloaded from https://github.com/eugeneware/ffmpeg-static/blob/master/download-binaries/index.sh
# on 7/21/2026 - used for downloading ffmpeg binaries to include in Mac and Windows builds.
# Stripped out of unnecessary stuff and simplified output for this folder structure.

set -e -u -o pipefail
cd $(dirname $0)

set +e
tar_exec=$(command -v gtar)
if [ $? -ne 0 ]; then
	tar_exec=$(command -v tar)
fi
if [ -z "$tar_exec" ]; then
	1>&2 echo "no tar executable found"
	exit 1
fi
# https://rtfmp.wordpress.com/2017/03/31/difference-7z-7za-and-7zr/
p7zip_exec=$(command -v 7zr)
if [ $? -ne 0 ]; then
	p7zip_exec=$(command -v 7zz)
fi
if [ $? -ne 0 ]; then
	p7zip_exec=$(command -v 7z)
fi
if [ -z "$p7zip_exec" ]; then
	1>&2 echo "no p7zip executable found"
	exit 1
fi
set -e
echo using tar executable at $tar_exec
echo using 7z executable at $p7zip_exec

mkdir -p bin

download () {
	# todo: use https://gist.github.com/derhuerst/745cf09fe5f3ea2569948dd215bbfe1a ?
	curl -f -L -# --compressed -A 'https://github.com/eugeneware/ffmpeg-static binaries download script' -o "$2" "$1"
}

set -x # todo: remove

echo 'windows x64'
echo '  downloading from github.com/GyanD/codexffmpeg'
# todo: 404
download 'https://github.com/GyanD/codexffmpeg/releases/download/6.1.1/ffmpeg-6.1.1-essentials_build.7z' win32-x64.7z
echo '  extracting'
tmpdir=$(mktemp -d)
$p7zip_exec e -y -bd -o"$tmpdir" win32-x64.7z >/dev/null
mv "$tmpdir/ffmpeg.exe" win32-x64/ffmpeg.exe
chmod +x win32-x64/ffmpeg.exe
mv "$tmpdir/LICENSE" win32-x64/ffmpeg.LICENSE
mv "$tmpdir/README.txt" win32-x64/ffmpeg.README
rm win32-x64.7z

echo 'darwin x64'
echo '  downloading from evermeet.cx'
download $(curl 'https://evermeet.cx/ffmpeg/info/ffmpeg/6.1.1' -fsS| jq -rc '.download.zip.url') ffmpeg-darwin-x64.zip
echo '  extracting'
unzip -o -d darwin-x64 -j ffmpeg-darwin-x64.zip ffmpeg
chmod +x darwin-x64/ffmpeg
curl -fsSL 'https://git.ffmpeg.org/gitweb/ffmpeg.git/blob_plain/HEAD:/LICENSE.md'  -o darwin-x64/ffmpeg.LICENSE
curl -fsSL 'https://evermeet.cx/ffmpeg/info/ffmpeg/release' | jq --tab '.' >darwin-x64/ffmpeg.README
rm ffmpeg-darwin-x64.zip

echo 'darwin arm64'
echo '  downloading from osxexperts.net'
download 'https://www.osxexperts.net/ffmpeg6arm.zip' ffmpeg-darwin-arm64.zip
echo '  extracting'
unzip -o -d darwin-arm64 -j ffmpeg-darwin-arm64.zip ffmpeg
chmod +x darwin-arm64/ffmpeg
curl -fsSL 'https://git.ffmpeg.org/gitweb/ffmpeg.git/blob_plain/n6.1.1:/LICENSE.md'  -o darwin-arm64/ffmpeg.LICENSE
curl -fsSL 'https://git.ffmpeg.org/gitweb/ffmpeg.git/blob_plain/n6.1.1:/README.md'  -o darwin-arm64/ffmpeg.README
rm ffmpeg-darwin-arm64.zip