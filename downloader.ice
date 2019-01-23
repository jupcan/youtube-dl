module Downloader {
  sequence<string> SongList; //list of songs
  enum Status {PENDING, INPROGRESS, DONE, ERROR}; //states for a task

  struct ClipData {
    string URL;
    Status status;
  };

  exception SchedulerAlreadyExists {};
  exception SchedulerNotFound {};
  exception SchedulerCancelJob {};

  interface Transfer { //handle a file transfer
    string recv(int size);
    void end();
  };

  interface DownloadScheduler {
    SongList getSongList();
    ["amd", "ami"] void addDownloadTask(string url) throws SchedulerCancelJob;
    ["ami"] Transfer* get(string song);
    // Optional
    void cancelTask(string url);
  };

  interface SchedulerFactory {
    DownloadScheduler* make(string name) throws SchedulerAlreadyExists;
    void kill(string name) throws SchedulerNotFound; //optional
    int availableSchedulers();
  };

  interface ProgressEvent { //status handling
    void notify(ClipData clipData);
  };

  interface SyncEvent { //sync handling
    void requestSync();
    void notify(SongList songs);
  };
};
