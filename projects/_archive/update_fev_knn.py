import pathlib

path = pathlib.Path("bench.py")
text = path.read_text(encoding="utf-8")

# Add KNN to FEV simple fits.
marker = '''        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
    }'''
insertion = '''        "subband_d1": (fit_subbands, lambda m,h: pred_subband(m,h,"d1")),
        "knn_forecaster": (fit_knn_forecaster, pred_knn_forecaster),
    }'''
if 'fits_simple' in text and 'knn_forecaster' not in text.split('def main(', 1)[1].split('def main_fev', 1)[0]:
    if marker not in text:
        raise RuntimeError("Could not find FEV fits_simple marker")
    text = text.replace(marker, insertion, 1)

# Add KNN to FEV Pool A.
marker = '        poolB=poolA+["subband_cA1","subband_d1"]'
insertion = '''        poolI=poolA+["knn_forecaster"] if _HAS_KNN else poolA
        poolI=[n for n in poolI if n in P_dict]
        poolB=poolA+["subband_cA1","subband_d1"]'''
if 'poolI=poolA+["knn_forecaster"]' not in text:
    if marker not in text:
        raise RuntimeError("Could not find FEV poolB marker")
    text = text.replace(marker, insertion, 1)

# Add Pool I output to FEV.
marker = '        out(f"  Pool A blend {maeA:.4f}  B {maeB:.4f}  C {maeC:.4f}")'
insertion = '''        maeI=pool_blend_mae(P_dict,A_true,poolI) if "knn_forecaster" in P_dict else float("nan")
        if _HAS_KNN and "knn_forecaster" in P_dict: out(f"  Pool I (KNN Feature) blend {maeI:.4f}")
        out(f"  Pool A blend {maeA:.4f}  B {maeB:.4f}  C {maeC:.4f}")'''
if 'Pool I (KNN Feature) blend' not in text:
    if marker not in text:
        raise RuntimeError("Could not find FEV pool output marker")
    text = text.replace(marker, insertion, 1)

# Add Pool I to aggregate output.
marker = '    out(f"meanA {meanA:.4f} meanB {meanB:.4f} meanC {maeC:.4f} winsB {winsB}/{len(task_results)} rankB {mean_rankB:.2f}")'
# use actual line from current file if marker differs
if marker not in text:
    marker = '    out(f"meanA {meanA:.4f} meanB {meanB:.4f} meanC {meanC:.4f} winsB {winsB}/{len(task_results)} rankB {mean_rankB:.2f}")'
insertion = '''    maesI=[i for _,_,_,i in task_results]
    meanI=float(np.nanmean(maesI)) if maesI else float("nan")
    winsI=sum(1 for a,i in zip(maesA,maesI) if i<a)
    out(f"meanA {meanA:.4f} meanB {meanB:.4f} meanC {meanC:.4f} meanI {meanI:.4f} winsB {winsB}/{len(task_results)} winsI {winsI}/{len(task_results)} rankB {mean_rankB:.2f}")'''
if 'meanI ' not in text:
    if marker not in text:
        raise RuntimeError("Could not find FEV aggregate output marker")
    text = text.replace(marker, insertion, 1)

# Update FEV result tuple and tuple unpacking.
text = text.replace('task_results.append((maeA,maeB,maeC))', 'task_results.append((maeA,maeB,maeC,maeI))')
text = text.replace('maesA=[a for a,_,_ in task_results]; maesB=[b for _,b,_ in task_results]; maesC=[c for _,_,c in task_results]', 'maesA=[a for a,_,_,_ in task_results]; maesB=[b for _,b,_,_ in task_results]; maesC=[c for _,_,c,_ in task_results]; maesI=[i for _,_,_,i in task_results]')
text = text.replace('for a,b,c in zip(maesA,maesB,maesC):', 'for a,b,c,i in zip(maesA,maesB,maesC,maesI):')
text = text.replace('order=sorted([(a,"A"),(b,"B"),(c,"C")])', 'order=sorted([(a,"A"),(b,"B"),(c,"C"),(i,"I")])')
text = text.replace('"winsB":winsB,"mean_rankB":mean_rankB', '"winsB":winsB,"winsI":winsI,"meanI":meanI,"mean_rankB":mean_rankB')

path.write_text(text, encoding="utf-8")
print("Added KNN to FEV benchmark")
