Couch Ripper Kodi Addon

About:
Like many others, I use Kodi and I like to rip my movies/TV shows to my library
from DVDs and Blu-ray discs. I had been doing this with a few scripts and wanted
to create a Kodi interface to make this a little smoother process. Couch Ripper
is designed to do just that. This project is still very alpha.

Pre-Requisites:
Couch Ripper utilizes MakeMKV <http://www.makemkv.com/> and HandBrake
<https://handbrake.fr/> to do the actual ripping and encoding of DVDs and
Blu-rays, so these must be installed prior to it working.

MakeMKV:
MakeMKV is the software responsible for ripping, decrypting and encoding the video.
It is proprietary software, and costs $50 for a license, but is free to use
while it is in beta. They have stated that once it leaves beta, DVD ripping will
continue to be free, while Blu-ray ripping will require a license. During the beta,
you can get the current license from <http://www.makemkv.com/forum2/viewtopic.php?f=5&t=1053>
which needs to be updated every 60 days. You can also show your support and
purchase a full license (which will not change through versions or updates) for
the software on their website <http://www.makemkv.com/>.

Installation - Ubuntu:
sudo add-apt-repository ppa:heyarje/makemkv-beta
sudo apt-get update
sudo apt-get install makemkv-bin makemkv-oss

Installation - Windows/Mac
http://www.makemkv.com/download/

Open the MakeMKV GUI and enter the key from the above-mentioned forum post, or
your purchased license.

HandBrake:
HandBrake transcodes the files output by MakeMKV and compresses them to their
final format. HandBrake is free and open-source software.

Installation - Ubuntu (Do not use the version in the Ubuntu repos):
sudo add-apt-repository ppa:stebbins/handbrake-releases
sudo apt-get update
sudo apt-get install handbrake-cli

Installation - Windows/Mac
https://handbrake.fr/downloads2.php

Setup:
I have tried to make Couch Ripper both easy to use and flexible. All of the defaults
are pretty sane for a great quality movie with a small file size. The paths to the
executables and folders have no defaults though, so those must be set prior to use.
When you open the config, you will see a defaults section and 10 separate profiles.
Set the defaults first, then you can use them in each profile. I like to use
several different profiles, like Movies, TV Shows, Foreign Films, Black and White, etc.
To use the default value for a setting in one of the profiles, either select
default from the dropdown, or leave it blank. All profiles are set to use the
values you set in the defaults section when they are created by default.

Pretty Name................The name of the profile that will be shown in the
                           selection dialog when you run Couch Ripper.
Enabled....................Whether or not this profile should be shown in the
                           selection dialog when you run Couch Ripper.
Path to MakeMKVCon.........Required. Path to the makemkvcon executable
                           (/usr/bin/makemkvcon on Ubuntu)
Path to HandBrakeCLI.......Required. Path to the HandbrakeCLI executable
                           (/usr/bin/HandBrakeCLI on Ubuntu)
Temporary Folder...........Required. Path to temporary folder for initial rips.
                           This folder will need at least 60GB free to store them.
Destination Folder.........Required. Path to where you want the final videos.
                           I do not suggest making this the same path as your
                           library, as the filenames will need cleanup.
CPU Priority...............Ripping and encoding videos is very CPU intensive.
                           Setting this to Normal or High may make the process
                           faster, but will likely leave your PC unoperable in the
                           meantime. Settings this to Low should allow you to use
                           the regular functions of Kodi in the meantime.
Resolution.................This is the maximum resolution. Videos with a higher
                           resolution will be reduced to this. Videos with a lower
                           resolution are unaffected.
Quality....................Quality setting. High is recommended, but if quality is
                           not a concern, and disk space is, choose another value.
Minimum Title Length.......Since MakeMKV works by ripping all video tracks above
                           a certain length, instead of picking the largest one,
                           we need to set a minimum title length, otherwise it
                           will rip all the previews, features, etc. A sane default
                           for movies is 45, for TV shows 8.
Native Language............This is the language YOU speak. This setting makes sure
                           that audio and subtitle tracks for your language are ripped,
                           if available. In the case of foreign films where your
                           language is not available, it will rip the language of
                           the movie instead.
Foreign Audio..............This setting is useful if you like to watch foreign
                           movies with subtitles in their native language. It grabs
                           all audio tracks available. If you do not like watching
                           foreign films with subtitles, do not use this option.
                           By setting the "Native Language" option above, your
                           audio and subtitles will be ripped by default, if
                           available.
Encode After Rip...........As stated before, the process is split in two processes.
                           First, a video is ripped, then it is encoded. Most users
                           will want to leave this as True. The only reason to
                           change it is if you wanted to encode your videos with
                           another application, or perhaps batch encode them when
                           your PC is not used, etc.
Eject After................Choose when (if ever) to eject a disc.
Notify After Rip...........Display a notification in Kodi after ripping a disc.
                           Notification will be automatically dismissed. Dialog
                           will pop up a notification that requires you to click
                           OK to dismiss it. This is helpful if you won't be
                           around to see the notification.
Notify After Encode........Display a notification in Kodi after encoding a movie.
                           Notification will be automatically dismissed. Dialog
                           will pop up a notification that requires you to click
                           OK to dismiss it. This is helpful if you won't be
                           around to see the notification.
Clean Up Temp Folder On
..Success..................Delete temporary files after a successful encode. Most
                           users would want to allow this, unless you are
                           experiencing issues.
Black and White............If a movie is black and white, this will tell the
                           encoder not to produce colors, which can reduce green
                           tinge or rainbow shimmering in black and white encodes.
                           DO NOT use this for videos that are in black and white
                           with partial color, such as Sin City.
Drive ID...................Numerical drive ID. If you have more than one optical
                           drive you may need to specify the correct drive here.
                           You can use Identify Drives to get the IDs.
Additional HandBrakeCLI
..Arguments................You can enter any additional arguments for HandBrakeCLI
                           here. Useful for audio settings and such that are not
                           handled by Couch Ripper. NOTE: Entering arguments here
                           that conflict with the arguments set by Couch Ripper
                           will probably end badly.
Identify Drives............You can use this to find out the numerical ID for your
                           optical drives. Just make sure to have a disc in the
                           drive(s) you want an ID for.
Show MakeMKVCon Command....This just displays the MakeMKVCon command that will be
                           run. Useful when debugging or using advanced options.
Show HandBrakeCLI Command..This just displays the MakeMKVCon command that will be
                           run. Useful when debugging, using advanced options, or
                           if you want to schedule encodings.


Usage:
After setting up Couch Ripper and creating a profile or two, all you have to do
is launch it. It will then bring up a dialog to choose the profile you want to
use. After selecting a profile, it will rip and encode the video(s) for you.
That's it!

CD Part of icon derived from work by gentleface.com
Couch part of icon derived from work by http://lethalnik-art.deviantart.com, http://minimalcustomizers.deviantart.com

TODO: Create encoding scheduler
Add Manual Naming Option
Add Renaming Options
If only title, remove txx in filename
Use strings.po
