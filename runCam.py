# live webcam prevewing
# arg1: prev, argv2: ms_interval (80)
# fig - click: pause, z: save frame
# motion detection
# argv1: diff, argv2: delay (5), threshold (1m), autosave (F), savediff (F), preview (F)

import cv2, time, sys, datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def takePic(rep=False):
    if rep == True:
        for i in range(5):
            img = cam.read()[1]
    img = cam.read()[1]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def savePic(direct, img, prefix='', suffix=''):
    filename = '%s%s%s%s.jpg' %(direct, prefix, datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S'), suffix)
    cv2.imwrite(filename, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print('%s saved.' %filename)

def camPreview(cam, ms_interval):
    direct = '/mnt/user/cam/pics/snapshots/'
    #if len(sys.argv) == 1:
    #    ms_interval = 80 # lowest 65ms
    #else:
    #    ms_interval = int(sys.argv[1])
    print(' interval: %d ms' %ms_interval)

    # create fig
    fig = plt.figure()
    #plt.axis('off')
    ax = fig.add_subplot(111)
    im = ax.imshow(img)

    def updatefig(*args):
        a = time.time()
        global img
        img = takePic()
        im.set_array(img)
        b = time.time()
        print b-a
        return im

    def on_click(event):
        # mouse clicks pause/unpause 
        if ani.running == True:
            print(' click: stop')
            ani.event_source.stop()
        else:
            print(' click: start')
            ani.event_source.start()
        ani.running ^= True

    def on_key(event):
        # press z key to autosave frame
        if event.key == 'z':
            savePic(direct, img, prefix='snap_')

    ani = animation.FuncAnimation(fig, updatefig, interval=ms_interval, save_count=1)
    ani.running = True
    cid1 = fig.canvas.mpl_connect('button_press_event', on_click)
    cid2 = fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()

def runBg(direct):
    print(' collecting bg...')
    time.sleep(5) # wait 5s to move out of way
    bg = takePic(True)
    savePic(direct, bg, 'm_', '_bg')
    return bg

def takeDiff(cam, bg, direct, delay, threshold, autosave, savediff):
    ms_interval = 500 + 1000*delay
    
    #print ' collecting pic..'
    # take diff
    time.sleep(delay)
    img = takePic(True)
    img_diff = cv2.absdiff(img, bg)
    diff = img_diff.sum()
    print('%d total' %diff)
    if diff > threshold:
        global counter
        counter = counter + 1
        print(counter)
        if autosave == True:
            savePic(direct, img, 'm_', '_px' + str(diff))
            if savediff == True:
                savePic(direct, img_diff, 'm_', '_diff')
        elif autosave == False:
            if raw_input(' save pic? (y/n) ') == 'y':
                savePic(direct, img, 'm_', '_px' + str(diff))
                #savePic(direct, img, 'm_')
                if savediff == True:
                    savePic(direct, img_diff, 'm_', '_diff')
    elif diff < threshold:
        #global counter
        #counter = 0 
        pass
    return img, img_diff

def autodetect(cam, delay, threshold, autosave, savediff, preview):
    # for motion detection
    #delay = 10 # acquisition rate
    #threshold = 4*10**6
    #autosave = True
    #savediff = False
    print('delay: %d s, threshold: %d px, autosave: %s, savediff: %s, preview: %s' %(delay, threshold, autosave, savediff, preview))

    direct = '/mnt/user/cam/pics/motion/'
    bg = runBg(direct)
    base = baseThreshold(bg)
    if threshold < base:
        threshold = base
        print(' threshold changed to base')
    if preview == True:
        fig = plt.figure()
        #plt.axis('off')
        img = takePic()
        ax1 = fig.add_subplot(211)
        im1 = ax1.imshow(img)
        ax2 = fig.add_subplot(212)
        im2 = ax2.imshow(img)
        ax1.set_title('%d threshold' %threshold)
    
    global counter
    counter = 0
    counter_lim = 10
    try:
        while True:
            if counter == counter_lim:
                counter = 0
                bg = runBg(direct)
                threshold = baseThreshold(bg)*2
                if preview == True:
                    ax1.set_title('%d threshold' %threshold)

            img, img_diff = takeDiff(cam, bg, direct, delay, threshold, autosave, savediff)
            if preview == True:
                im1.set_array(img)
                im2.set_array(img_diff)
                #ax1.set_title(base)
                plt.pause(0.1)
    except KeyboardInterrupt:
       print('\n stop detection')

def baseThreshold(bg, delay=5):
    time.sleep(delay) 
    img = takePic(True)
    img_diff = cv2.absdiff(img, bg)
    base = img_diff.sum()
    base2 = base * 1.5 # darkness have less pixels, requires less threshold, what is min-max? 100k- ~4m?
    print('%d base, %d threshold' %(base, base2))
    return base2

#############
# MAIN CODE #
#############
lowres = True
#lowres = False

if sys.argv[1] == 'prev':
    livepreview = True
    livediff = False
    print(' preview on')
elif sys.argv[1] == 'diff':
    livediff = True
    livepreview = False
    print(' motion on')
else:
    print(' ERROR, REQUIRES prev or diff')

# init (always)
cam = cv2.VideoCapture(0)
if lowres == True:
    cam.set(3, 100)
    cam.set(4, 100)
img = takePic()

# options
if livepreview == True:
    if len(sys.argv) == 3:
        ms_interval = int(sys.argv[2])
    else:
        ms_interval = 80
    camPreview(cam, ms_interval)

if livediff == True:
    if len(sys.argv) == 7 and sys.argv[6] == 't':
        preview = True
    else:
        preview = False
    if len(sys.argv) >= 6 and sys.argv[5] == 't':
        savediff = True
    else:
        savediff = False
    if len(sys.argv) >= 5 and sys.argv[4] == 't':
        autosave = True
    else:
        autosave = False
    if len(sys.argv) >= 4 and sys.argv[3] >= 0:
        try:
            threshold = int(sys.argv[3])
        except:
            threshold = 1*10**6
    else:
        threshold = 1*10**6
    if len(sys.argv) >= 3 and sys.argv[2] >= 0:
        try:
            delay = int(sys.argv[2])
        except:
            delay = 5
    else:
        delay = 5

    autodetect(cam, delay, threshold, autosave, savediff, preview)





